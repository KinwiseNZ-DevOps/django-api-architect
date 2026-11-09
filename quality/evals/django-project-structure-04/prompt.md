---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/orders/services.py:
```python
from apps.billing.models import Invoice, Charge

def order_pay(*, order):
    inv = Invoice.objects.get(order=order)
    Charge.objects.create(invoice=inv, amount=order.total)
```

Request: Is this import fine? Also our React app on app.example.com now needs to call the API from the browser.
