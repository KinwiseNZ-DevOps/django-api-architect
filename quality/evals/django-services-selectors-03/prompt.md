---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Services use keyword-only arguments and raise Django's ValidationError; APIs are thin and call services; selectors do the reads. The apps are apps/billing, apps/orders, apps/accounts and a core apps/common. Optional domain packs are enabled through an OPTIONAL_APPS environment variable and each has a manifest.py. Answer from this description and the code below.

Existing code:
```python
# apps/orders/services.py
def order_cancel(*, order):
    if order.status == 'shipped':
        raise ValidationError('Shipped orders cannot be cancelled.')
    order.status = 'cancelled'
    order.full_clean()
    order.save()
```

Request: Add the eligibility rule to the serializer too, so the API can show a friendly message.
