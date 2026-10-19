---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code:
```python
# apps/orders/services.py
def order_create(*, customer, items):
    order = Order(customer=customer)
    order.full_clean()   # raises django.core.exceptions.ValidationError
    order.save()
    return order
```
settings.py has REST_FRAMEWORK = {} with no EXCEPTION_HANDLER.

Request: My service calls full_clean() and an invalid request returns a 500. There is no exception handler in the project.
