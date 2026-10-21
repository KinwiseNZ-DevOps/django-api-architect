---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API using a service layer, a multi-stage Dockerfile with Gunicorn, Celery workers, settings read from environment variables and PostgreSQL. Answer from this description.

The API runs on ECS Fargate behind an Application Load Balancer. The target group shows unhealthy with reason Target.ResponseCodeMismatch, and the container logs show 400 Bad Request for GET /healthz/ from a private IP address. ALLOWED_HOSTS only lists api.example.com.

Request: Fix the health check.
