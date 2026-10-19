---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/tasks.py:
```python
@shared_task(bind=True)
def payment_capture_task(self, payment_id):
    try:
        payment_capture(payment_id=payment_id)
    except ProviderError as exc:
        raise self.retry(exc=exc, countdown=5)
```

Request: Make the payment task retry indefinitely until it succeeds.
