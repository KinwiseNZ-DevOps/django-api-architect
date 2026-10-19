---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

A new apps/loyalty pack is being added. Existing apps/billing/manifest.py declares required_settings=['STRIPE_API_KEY'], and the repo has an .env.example file.

Request: The new pack needs an API key for an external service. Where does it go?
