---
name: django-celery
description: >
  Governs Celery task structure, retries, transaction-safe task triggering,
  webhook dispatch chains, periodic tasks and Celery configuration. Use when
  writing or changing tasks, retry behaviour, task triggering inside
  transactions, or webhook processing. Do not use for the business logic
  tasks call (django-services-selectors) or the tests that cover them
  (django-testing).
---

# Django Celery Tasks

Stance: tasks are interfaces, not logic. A task fetches its inputs, calls a service, and handles retry and failure. Everything else is flexible.

## Gate

| Situation | Action |
|---|---|
| New or changed task, or new task trigger inside a transaction | Continue |
| Business logic wanted in the task body | Push back; put it in a service |
| Heavy or slow work happening inside an HTTP request | Continue; move it to a task |

## Steps

1. **Detect.** Find the app's `tasks.py` (or `tasks/` package). Confirm the shape: `@app.task(bind=True, max_retries=..., default_retry_delay=...)`, thin bodies, retry handling in the task, services imported inside the function body, tasks imported at module level with a `_task` alias when names collide.
2. **Fix.**
   - Write the task as fetch-then-delegate; retries use `self.retry(exc=..., countdown=...)` with a bounded `max_retries` and an increasing countdown; the exhausted case goes to an `on_failure` callback named `_<task_name>_failure`, which calls a service.
   - Inside `@transaction.atomic` services, trigger with `transaction.on_commit(lambda: task.delay(...))`, never directly. `on_commit` callbacks take no arguments (bind with a lambda or `functools.partial`), run immediately if there is no open transaction, and are discarded if the transaction rolls back. With the default `robust=False`, an exception in one callback skips the later ones registered in the same transaction.
   - Webhook providers: one endpoint that verifies the signature (400 on failure), logs the event idempotently in an event table inside a transaction, dispatches a dispatcher task, and acknowledges 200 within the provider's timeout. The dispatcher maps event types to handlers, skips already-processed events, marks `processed_at` after success, and retries on handler failure. Handlers call idempotent service upserts.
3. **Verify.** Task tests confirm delegation, retry-on-failure and exhaustion behaviour (see django-testing); no task duplicates logic that exists in a service.

## Hard rules

- Tasks call services; they contain no business logic. Mechanism: symptom is the same rule implemented differently in a task and an API; cause is logic written where it is triggered; fix is one service called by every interface.
- Always trigger tasks via `transaction.on_commit` inside transactions. Mechanism: symptom is intermittent "object does not exist" errors in workers; cause is the task running before the transaction commits; fix is the on_commit hook.
- Import services inside the task body and tasks at module level (aliased `_task` on name collision). Mechanism: the reverse ordering creates circular imports between tasks and services.
- Bounded retries only; unbounded retry loops mask permanent failures. Mechanism: a poison message otherwise retries forever, consuming workers.

## Configuration

`config/celery/app.py` stays minimal: set `DJANGO_SETTINGS_MODULE` before creating the app, `config_from_object("django.conf:settings", namespace="CELERY")`, `autodiscover_tasks()`. Celery settings come from a settings partial through a builder function, `CELERY_` prefixed. Periodic tasks use Celery Beat with the `DatabaseScheduler` and a `setup_periodic_tasks` management command holding every schedule in one place (cron schedules, linked to crontab.guru), run as part of deploys. Worker and beat run as separate containers locally.

## References

Theory source: the public Django Styleguide, https://github.com/HackSoftware/Django-Styleguide (celery section). `on_commit` behaviour: https://docs.djangoproject.com/en/6.1/topics/db/transactions/

## Next

- The services tasks call: [django-services-selectors](../django-services-selectors/SKILL.md)
- Testing tasks: [django-testing](../django-testing/SKILL.md)
