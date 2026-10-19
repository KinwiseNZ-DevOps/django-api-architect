---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code:
```python
# apps/orders/selectors.py
def order_list_for_user(*, user):
    return Order.objects.filter(customer__user=user).select_related('customer')
```
The test suite uses pytest-django.

Request: Mock the ORM so the selector tests run fast without a database.
