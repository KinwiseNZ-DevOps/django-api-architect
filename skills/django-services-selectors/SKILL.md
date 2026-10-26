---
name: django-services-selectors
description: >
  Governs the service and selector layer: writing business logic, validation
  placement, transactions, and update helpers. Use when writing or changing a
  service or selector, a refund or similar multi-step write, row-level filtering
  or ownership checks, model validation, or deciding where a business rule
  belongs, including when asked to duplicate a rule in a serializer or view. Do
  not use for API classes that call them (django-apis-serializers) or for task
  retry and scheduling mechanics (django-celery).
---

# Django Services and Selectors

Stance: services write, selectors read, and both are plain functions with keyword-only arguments. Class-based services are the exception, for multi-step flows or shared helper namespaces.

## Hard rules

- Validate at the lowest level that can enforce it: database constraints first, model `clean` (called via `full_clean` in the service) for simple cross-field rules on the model's own fields, service-level checks for anything complex or relational. `Model.objects.create()` bypasses `full_clean`, so construct then save. Mechanism: symptom is bad data reachable through some write path; cause is validation living only in one caller; fix is constraint or validated service as the single path.
- Business logic never lives in APIs, serializers, model `save`, custom managers or signals. Signals are only for decoupling things that should not know about each other and for cache invalidation. Mechanism: implicit triggers make data flow untraceable.
- Multi-property derivations that must change together go in one model method or service, never in two places. Mechanism: drift between duplicated derivations.
- Never catch an exception from inside an `atomic()` block without immediately exiting it. Mechanism: Django marks the transaction broken on a database error regardless of whether the exception is caught; any further query before the block exits raises `TransactionManagementError` instead of the original error. Fix: catch around the block, or isolate the risky step in its own nested `atomic()` and catch immediately outside that.
- Never make a network or external API call inside an open `atomic()` block. Mechanism: the transaction holds database resources for as long as it is open, so a slow external call (or its retries and timeouts) holds them for that long too. Fix: call the external system first, then open a short transaction for the local write once its result is known.
- A bulk write (`update()`, `delete()`, `bulk_create()`, `bulk_update()`) does not call `save()`/`delete()` or send signals. Mechanism: any side effect a service relies on through a signal or an overridden `save()` silently does not run for rows touched this way. Fix: give the bulk path its own explicit side effect, or fall back to the per-instance path when the side effect matters.
- Never build a raw SQL string with formatting, and never quote a `%s` placeholder. Mechanism: `Manager.raw()` and `connection.cursor()` are only safe from SQL injection when the value is passed through `params` with the placeholder left unquoted; string formatting or quoting it defeats that regardless of where the value came from. Fix: `params=[value]` with an unquoted `%s`, never `% value` or `'%s'`.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| New or changed write path, read path, or validation rule | Continue |
| Logic is a simple derived value on one model's own fields | A model property or `clean` may be the better home |
| Logic spans relations, queries extra data, or risks N+1 when serialised | Continue; it belongs here, not on the model. See [query-patterns.md](references/query-patterns.md) |
| A bulk update, bulk create, or a raw SQL query is being written | Continue; see [query-patterns.md](references/query-patterns.md) for the signal and injection gotchas specific to each |

## Steps

1. **Detect.** Open the app's `services.py` and `selectors.py`. Check the conventions: keyword-only arguments, type annotations, `<entity>_<action>` naming (`user_create`, `invoice_list_for_user`), selectors scoped to the caller (`*_for_user(*, user)`).
2. **Fix.** Least invasive first:
   - Write path: construct the instance, `full_clean()`, `save()`, then call other services; return the object. Keep everything for one domain action in one traceable place.
   - Read path: filter inside the selector, enforcing ownership in the query itself (`billing_profile__user=user`) so a caller cannot leak other users' rows; return querysets for lists, objects for get.
   - Updates: push field-only writes through a generic `model_update(instance, fields, data)` helper; keep only side-effect logic in the specific update service; pass `update_fields` on save.
   - Wrap multi-step writes in `@transaction.atomic`; schedule follow-up work with `transaction.on_commit(lambda: task.delay(...))` (see django-celery). Catch exceptions around the `atomic` block, never inside it: see [transactions.md](references/transactions.md) for why a caught exception inside the block still leaves the transaction broken.
   - Calls to external systems belong in services, never in APIs; make third-party upserts idempotent with `update_or_create` keyed on the provider's object id. Make the external call before opening the transaction, not inside it, so a slow or failed call never holds a database transaction open.
3. **Verify.** Exhaustive service tests exist (see django-testing), including the failure branches; no duplicate copies of the same rule exist in an API or serializer.

## References

- [transactions.md](references/transactions.md): the poisoned transaction, savepoint nesting, on_commit with savepoints, model state after rollback, ATOMIC_REQUESTS scope, keeping transactions short.
- [query-patterns.md](references/query-patterns.md): evaluating a queryset once, select_related/prefetch_related, defer/only, bulk methods skipping signals, raw SQL parameterization, and search.

Theory source: the public Django Styleguide, https://github.com/HackSoftware/Django-Styleguide (services, selectors, models sections). Transaction semantics: https://docs.djangoproject.com/en/stable/topics/db/transactions/ . Query optimisation, raw SQL and search: https://docs.djangoproject.com/en/stable/topics/db/

## Next

- Testing these services: [django-testing](../django-testing/SKILL.md)
- Scheduling the side effects: [django-celery](../django-celery/SKILL.md)
