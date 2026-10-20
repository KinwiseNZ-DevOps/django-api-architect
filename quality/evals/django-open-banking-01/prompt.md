---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

The project just added apps/open_banking with a BlinkPay adapter behind a PaymentProvider interface (create_single_payment, get_payment_status), used from apps/orders/services.py.

Request: Create an endpoint where the frontend posts the amount and reference to charge, and we create a BlinkPay payment for exactly what it sends.
