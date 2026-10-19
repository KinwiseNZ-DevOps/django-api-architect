---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing Dockerfile (single stage, python:3.13-slim) runs `pip install -r requirements/production.txt` and `python manage.py collectstatic --noinput`, which fails because SECRET_KEY is not set at build time.

Request: Pass our SECRET_KEY and database password as ARG values in the Dockerfile so the build can run collectstatic.
