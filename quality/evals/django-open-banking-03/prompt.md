---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/open_banking/services.py has payment_create(*, order, idempotency_key) which calls the BlinkPay adapter. A Celery task retries this service on a 5xx from BlinkPay.

Request: On retry, generate a fresh idempotency key each time so BlinkPay doesn't think it's a duplicate request.
