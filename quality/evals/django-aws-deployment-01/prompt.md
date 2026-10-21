---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API using a service layer, a multi-stage Dockerfile with Gunicorn, Celery workers, settings read from environment variables and PostgreSQL. Answer from this description.

The team asks where to host it on AWS. They already run the same image for the web app and for Celery workers, and want few servers to look after.

Request: Which AWS service should we use and why?
