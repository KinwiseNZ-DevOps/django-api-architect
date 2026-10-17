DJANGO API ARCHITECT ACTIVE (always-on). Apply to Django and DRF work in this session.

1. Read the project's own conventions first (AGENTS.md, settings, an existing app). Where they differ from these rules, the project wins.
2. Keep interfaces thin. APIs, serializers, tasks and commands validate input and call services. Business logic belongs in services (writes) and selectors (reads), never in views, serializers, model save, managers or signals.
3. Every app has the same shape: models, selectors, services, apis, tasks, urls, tests. A new domain is a pack, not an edit to a core app.
4. Settings come from environment variables. Required secrets have no default. Never commit .env; ship .env.example. Never edit a migration already applied elsewhere; add a new one.
5. Make the smallest correct change and verify it with the project's own tests. Say which checks ran and which did not.
6. For detail use the matching skill: django-project-structure, django-apis-serializers, django-services-selectors, django-testing, django-auth, django-celery, django-docker-images, django-docker-compose.
