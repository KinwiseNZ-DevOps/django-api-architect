---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/models.py:
```python
class Invoice(models.Model):
    customer = models.ForeignKey('billing.Customer', on_delete=models.CASCADE)
    total = models.FloatField()
```

Request: Review this model before we ship it.
