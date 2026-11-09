---
name: django-observability
description: >
  Use when adding or changing logging, a request or correlation id, error
  tracking such as Sentry, a health or readiness endpoint, uptime checks,
  performance monitoring or alerts for a Django API, including when asked to log
  request bodies, tokens or emails, to email logs, or to catch all exceptions.
  Governs how a Django API reports what it is doing and what went wrong. Do not
  use for the CloudWatch or load balancer setup itself (django-aws-deployment),
  release and incident process (django-release-governance) or test code
  (django-testing).
---

# Django Observability

Stance: logs say what happened, an error tracker says what broke, a health check says whether to send traffic, and an alert says a person must act. Each has one job. Which vendor provides each is flexible.

## Hard rules

- Never log secrets or personal data: passwords, tokens, OTP codes, full bank or card numbers, or request bodies. Log ids, not people. Mechanism: logs are copied to more systems and kept longer than the database, so a leaked value spreads; fix is to log identifiers and event names, and to add a logging filter that masks known keys.
- Send unhandled errors to an error tracker, not to log files or email. Mechanism: symptom is an error that nobody sees or the same error mailed a thousand times; cause is using logs as the alarm; fix is a tracker that groups repeats, records the request context and notifies a named owner. Configure it to leave personal data out by default.
- Give every request an id and put it on every log line and in the error report. Mechanism: without it a support case cannot be followed across services, tasks and logs.
- In containers, write logs to standard output and let the platform collect them. Mechanism: files inside a container disappear when it is replaced.
- Keep the liveness check cheap and free of dependencies, and put database and cache checks in a separate readiness check. Mechanism: if liveness checks the database, a short database blip fails every instance at once and the platform restarts all of them.
- Every alert has an owner and an action; an alert nobody can act on is deleted or tuned, and an alert is never muted forever. Mechanism: noisy or ignored alerts hide the real one.
- Never catch a blanket `except Exception` to keep going. Catch the specific exception, or let it reach the handler so the tracker sees it.
- Act only on what the user asked. Before answering or changing anything, open the relevant files and check what is already done; report only what you checked, never guess, and do not redo finished work. Reason: guesses and repeated work waste the user's credit.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| New or changed logging, request id, error tracking, health check or alert | Continue |
| Someone asks to log a request body, token, code or email address | Push back; log an id or an event name |
| Setting up CloudWatch, load balancer targets or ECS log drivers | Use [django-aws-deployment](../django-aws-deployment/SKILL.md) |
| Release steps, rollback or incident review | Use [django-release-governance](../django-release-governance/SKILL.md) |

## Steps

1. **Detect.** Find `LOGGING` in the settings, any logging helper, the middleware list, the error tracker setup, and the health endpoint. Note what the platform already collects.
2. **Fix.** Least invasive first:
   - Logging: one `LOGGING` dictionary in a settings partial, a console handler, one formatter that includes the request id, and `disable_existing_loggers` set to `False`. Name loggers by module (`logging.getLogger(__name__)`) so a level can be changed per area. Use levels honestly: `INFO` for business events, `WARNING` for recoverable oddities, `ERROR` for failures a person should see.
   - Request id: keep it in a `contextvars.ContextVar` (safe for threads and async), set it in a small middleware, return it in an `X-Request-ID` response header, and copy it into task headers or arguments so worker logs share it. Do not trust a client-sent id without checking its length and characters.
   - Error tracker: initialise it once at start-up with the environment name and release, link the release to the Git tag, turn personal data off, and add a scrubbing step for known keys. Tasks and management commands need the same setup as the web process.
   - Health: `/healthz/` for liveness (see django-aws-deployment) and a separate readiness path that checks the database and cache and returns 503 on failure. Leave both unauthenticated and uncached.
   - Uptime and performance: point an external uptime check at the readiness path, and track response time, request rate and error rate per endpoint. Throttled requests (429) are logged and counted so a limit set too low shows up.
   - Alerts: start with few, on symptoms users feel (error rate, slow responses, failed readiness, queue backlog), each with a named owner and a one-line first action.
3. **Verify.** Trigger a test error and see it in the tracker with the request id; confirm a log line carries the same id; confirm no secret appears in a sample of log output; confirm liveness stays green when the database is stopped and readiness goes red. Say which of these you could not run.

## Example

```python
import contextvars
import logging
import re
import uuid

request_id_var = contextvars.ContextVar("request_id", default="-")
_SAFE_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")


class RequestIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        supplied = request.headers.get("X-Request-ID", "")
        request_id = supplied if _SAFE_ID.match(supplied) else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        response["X-Request-ID"] = request_id
        return response


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True
```

Register the filter on the console handler and add `%(request_id)s` to the formatter. This middleware is synchronous; if the project serves async views, decorate it with Django's `sync_and_async_middleware`.

## References

Python logging cookbook: https://docs.python.org/3/howto/logging-cookbook.html . Django logging: https://docs.djangoproject.com/en/stable/topics/logging/ . Request-id pattern uses `contextvars`: https://docs.python.org/3/library/contextvars.html

## Next

- Hosting, log delivery and load balancer checks: [django-aws-deployment](../django-aws-deployment/SKILL.md)
- Release, rollback and incident review: [django-release-governance](../django-release-governance/SKILL.md)
- Task logging and retries: [django-celery](../django-celery/SKILL.md)
