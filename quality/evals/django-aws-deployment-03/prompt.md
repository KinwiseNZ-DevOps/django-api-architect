---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API using a service layer, a multi-stage Dockerfile with Gunicorn, Celery workers, settings read from environment variables and PostgreSQL. Answer from this description.

A teammate drafted an apprunner.yaml with the line DATABASE_URL: postgres://django:Passw0rd@mydb.example.rds.amazonaws.com/django in the env section and startup.sh runs python manage.py migrate before gunicorn. The service will scale to 4 instances.

Request: Review this and make it ready to deploy.
