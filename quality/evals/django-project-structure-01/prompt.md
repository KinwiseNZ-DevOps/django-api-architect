---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing apps/common/ and apps/billing/ are in place. apps/billing/manifest.py declares: app, name, optional, dependencies, required_settings, url_prefix, urlconf.

Request: Add a new loyalty domain feature to the backend.
