---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/selectors.py:
```python
def invoice_list_for_user(*, user):
    return Invoice.objects.filter(billing_profile__user=user)
```

Request: This list endpoint is slow. Cache it for everyone for an hour.
