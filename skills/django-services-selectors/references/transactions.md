# Transactions in services

Contents: the poisoned transaction, savepoints and nesting, on_commit and savepoints together, model state after rollback, ATOMIC_REQUESTS scope, keeping transactions short

Distilled from Django's own transaction documentation (https://docs.djangoproject.com/en/stable/topics/db/transactions/); check it directly for anything this file does not cover.

## The poisoned transaction

This is the single most common way a service breaks itself. Catching an exception inside an `atomic()` block does not undo the error for Django; it only hides it from Python.

```python
# wrong: looks handled, but the transaction is now broken
with transaction.atomic():
    parent.save()
    try:
        child.save()  # raises IntegrityError
    except IntegrityError:
        logger.warning("child save failed")
# any further query in this block now raises TransactionManagementError
```

After a database error inside an `atomic` block, that block's transaction (or savepoint) is marked broken even if the exception is caught. Running another query before the block exits raises `TransactionManagementError`, not the original error. Django only knows to roll back cleanly when the exception is allowed to propagate out of the `atomic` block itself.

**Fix: catch around the block, not inside it**, and open a fresh `atomic` block for whatever comes after:

```python
def child_create(*, parent, data):
    try:
        with transaction.atomic():
            child = Child(parent=parent, **data)
            child.full_clean()
            child.save()
    except IntegrityError as exc:
        raise ChildCreateError(str(exc)) from exc
    return child
```

If a single service genuinely needs to attempt something that might fail and keep going, wrap only the risky part in its own nested `atomic()` (a savepoint) and catch the exception immediately outside that inner block, not the outer one.

## Savepoints: what nesting actually buys you

The outermost `atomic()` opens a real transaction; every `atomic()` nested inside it is a savepoint, not a second transaction. Exiting a nested block cleanly releases its savepoint; an exception rolls back to it. The outer transaction, and anything committed before the inner block started, survives:

```python
with transaction.atomic():
    parent_create(...)
    try:
        with transaction.atomic():
            risky_step(...)  # only this is undone on failure
    except SomeError:
        handle(...)
    finish_up(...)  # parent_create()'s work is still there
```

Use this shape deliberately when one step in a multi-step write is allowed to fail without discarding the steps before it; for everything else, one `atomic()` per service call is simpler and easier to reason about.

## on_commit inside a rolled-back savepoint is silently dropped

A callback registered with `transaction.on_commit()` inside a nested `atomic()` only runs if both that savepoint survives and the outer transaction commits. If the savepoint is rolled back, the callback is discarded, even though execution continues and the outer transaction later commits successfully. This is usually what you want (don't email a customer about a step that was undone), but it means a callback registered before entering a nested block, and one registered inside it, can have different fates from the same service call. Keep `on_commit()` calls inside the same `atomic()` block as the write they report on, not hoisted above a nested block that might roll back.

## Model field values do not roll back

If a service mutates a Python object's fields before saving inside an `atomic()` block that then fails, the object's in-memory field values are not reverted when the database rolls back:

```python
order.status = "paid"
try:
    with transaction.atomic():
        order.save()
        take_payment(order)  # raises
except PaymentError:
    order.status = "pending"  # must be restored by hand; the DB already rolled back, the Python object did not
    raise
```

Treat a service's local object as untrustworthy after a caught failure inside the block it was saved in; re-fetch it from the database, or restore the fields that were changed, before using it again.

## ATOMIC_REQUESTS does not cover everything in the request

If a database has `ATOMIC_REQUESTS = True`, Django wraps the view's own execution in `atomic()`, nothing more. Middleware that runs before or after the view, and anything that generates a `StreamingHttpResponse`'s content, runs outside that transaction. Do not rely on `ATOMIC_REQUESTS` to make a side effect triggered from middleware, or from code that only runs while streaming a response, part of the same all-or-nothing unit as the view's own writes; wrap that code in its own explicit `atomic()` if it needs the same guarantee.

## Keep transactions short, and never call an external system inside one

An open transaction holds database-level resources (locks, in Postgres's case) for as long as it is open. A `atomic()` block that also makes a network call, an external API request, or any slow I/O holds those resources for the duration of that call, not just the database work:

```python
# wrong: the BlinkPay call (and any retry or timeout inside it) happens
# while the local database transaction is open
def payment_create(*, order, idempotency_key):
    with transaction.atomic():
        result = blinkpay_adapter.create_single_payment(...)  # network call
        Payment.objects.update_or_create(order=order, defaults={...})
    return result

# right: the external call happens with no transaction open; only the
# local write (fast, all-database) is wrapped
def payment_create(*, order, idempotency_key):
    result = blinkpay_adapter.create_single_payment(...)
    with transaction.atomic():
        Payment.objects.update_or_create(order=order, defaults={...})
    return result
```

This applies to any third-party call a service makes (see django-open-banking for the payment-provider case specifically), not only payment providers. If a step must be atomic with the external call's result (for example, the write must not happen at all if the call failed), that is a reason to call the external system first and only open the transaction once its result is known, not a reason to hold the transaction open across the call.
