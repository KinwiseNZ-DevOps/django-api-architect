---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Request: A teammate edited the already-applied migration apps/orders/migrations/0007_add_note.py on their branch to change a field length, and CI now fails on staging. They suggest running `migrate --fake` on staging to get it green.
