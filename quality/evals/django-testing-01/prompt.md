---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/services.py:
```python
def charge_create(*, user, amount_cents: int, currency: str = 'nzd') -> Charge:
    if amount_cents <= 0:
        raise ValidationError('Amount must be positive.')
    customer_id = stripe_customer_get_or_create(user=user)
    result = stripe.Charge.create(customer=customer_id, amount=amount_cents, currency=currency)
    return Charge.objects.create(user=user, provider_id=result.id, amount_cents=amount_cents)
```

Request: Add tests for the charge_create service.
