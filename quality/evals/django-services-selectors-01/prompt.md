---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing models: Refund(charge, amount_cents, reason), Charge(user, amount_cents, status). apps/billing/tasks.py has `refund_notification_task(refund_id)`.

Request: Write a service that issues a refund and notifies the customer.
