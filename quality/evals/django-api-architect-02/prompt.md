---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing layout: apps/reports/ has models.py (Report), selectors.py (report_list), services.py, apis.py, urls.py and tests/.

Request: We need a new CSV export endpoint for reports.
