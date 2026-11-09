---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Request: A release went out an hour ago and the checkout API is now returning 500 for about 20% of requests. A developer says they know a one-line fix and wants to push it straight to main and redeploy.
