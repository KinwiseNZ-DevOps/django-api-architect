---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/tasks.py:
```python
@shared_task
def send_statements():
    for user in User.objects.all():
        statement_send(user=user)

@shared_task
def charge_task(invoice):
    invoice_charge(invoice=invoice)
```

Request: Review these two tasks before they go to production.
