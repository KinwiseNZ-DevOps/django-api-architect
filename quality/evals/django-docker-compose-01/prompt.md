---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing docker-compose.yml:
```yaml
services:
  web:
    build: .
    depends_on: [db]
    command: gunicorn config.wsgi
  db:
    image: postgres:16
```

Request: Our web container crashes on first docker compose up because Postgres is not ready.
