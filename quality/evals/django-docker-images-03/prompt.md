---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Services use keyword-only arguments and raise Django's ValidationError; APIs are thin and call services; selectors do the reads. The apps are apps/billing, apps/orders, apps/accounts and a core apps/common. Optional domain packs are enabled through an OPTIONAL_APPS environment variable and each has a manifest.py. Answer from this description and the code below.

Existing Dockerfile (python:3.13-slim, gunicorn on port 8000) has no HEALTHCHECK. The API has a /health/ route. settings has ALLOWED_HOSTS from an env var, set to api.example.com in production with DEBUG off.

Request: Add a HEALTHCHECK that curls localhost on the API, it keeps reporting unhealthy.
