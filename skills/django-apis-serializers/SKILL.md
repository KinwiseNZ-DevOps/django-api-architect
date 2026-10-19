---
name: django-apis-serializers
description: >
  Governs DRF API classes, input and output serializers, filtering, pagination,
  and the JSON error contract. Use when writing or changing an endpoint, a
  serializer, a list filter, pagination, a 404 or validation error response, or
  an exception handler, including when asked to expose raw exceptions or to
  raise errors from a service. Do not use for the business logic those APIs call
  (django-services-selectors) or for login and token endpoints (django-auth).
---

# Django APIs and Serializers

Stance: APIs are frozen as thin interfaces: one APIView class per operation, validate, delegate, serialise. Serialisation strategy is flexible as long as input and output stay separate.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| New endpoint, or changes to an endpoint's contract | Continue |
| Business logic wanted inside the API (calculations, writes beyond delegation) | Push back; move it to a service |
| Change is only internal to a service the API calls | Route to django-services-selectors |

## Steps

1. **Detect.** Find the app's `apis.py` and `urls.py`. Confirm the existing shape: plain `APIView` per operation, `permission_classes` explicit, `@extend_schema` annotations feeding the OpenAPI schema, and one path per API with a named route.
2. **Fix.** Follow the house patterns, least invasive first:
   - Reads: a module-level output serializer shared by list and detail; the API calls a selector and returns `Serializer(data).data`.
   - Writes: nest `InputSerializer` and `OutputSerializer` in the API class; validate with `is_valid(raise_exception=True)`, resolve caller context, call the service with keyword arguments.
   - List filtering: the API owns a nested `FilterSerializer` validating query params, and passes `validated_data` to the selector, which does the actual filtering (typically with `django-filter`).
   - Pagination: apply through the pagination helper (limit/offset, `default_limit` 10, `max_limit` 50), returning `limit`, `offset`, `count`, `next`, `previous`, `results` in the body.
   - Detail: fetch via a user-scoped selector; catch `DoesNotExist` and return `{"detail": "Not found."}` with 404.
   - Permissions: set a restrictive global default in `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']` and override with `permission_classes` per API only where needed. Compose classes with `&`, `|` and `~` rather than writing new classes for simple combinations.
   - Object-level access: DRF's object permission checks do not run on list or create actions, so list access is enforced by the selector's user-scoped query and creates by the service. For detail APIs that fetch objects themselves, call `self.check_object_permissions(request, obj)` or rely on the user-scoped selector.
   - Throttling: use `ScopedRateThrottle` with a `throttle_scope` per API group and rates in `DEFAULT_THROTTLE_RATES`. Throttles use Django's cache; behind a proxy set `NUM_PROXIES` correctly.
   - Document every endpoint with `@extend_schema` (tags, summary, request, responses including error codes).
3. **Verify.** Endpoint tests pass; schema at `/api/schema/` renders; the response shape matches the error contract below.

## Hard rules

- One API class per operation; no generic views or viewsets. Mechanism: generic classes manage behaviour via serializers and hooks, which fragments logic and hides data flow; explicit classes stay greppable and simple.
- Serializers validate and shape data only; no business logic in serializers. Mechanism: hidden `create`/`update` overrides make writes untraceable.
- Errors always come back in the project's one JSON contract (validation as `{"field": ["message"]}` or the message-plus-extra shape; everything else as `detail`). Django's `ValidationError` must be converted to DRF's at the exception-handler boundary. Mechanism: symptom is 500s on model validation or inconsistent error shapes per endpoint; cause is Django and DRF exceptions reaching the client raw; fix is the normalising exception handler.
  - If the project has no such handler yet, add one before services start calling `full_clean()`: register `REST_FRAMEWORK["EXCEPTION_HANDLER"]` with a small function that wraps DRF's `exception_handler` and turns `django.core.exceptions.ValidationError` into `rest_framework.exceptions.ValidationError(exc.message_dict)` (or `exc.messages` when there is no field). Symptom without it: invalid data reaches the client as a 500, because Django's `ValidationError` is not a DRF exception.
- Never rely on DRF's default permissions. Mechanism: with `DEFAULT_PERMISSION_CLASSES` unset DRF applies `AllowAny`, so a forgotten `permission_classes` leaves an endpoint open; fix is a restrictive global default.
- Treat throttling as abuse control, not security. Mechanism: client IPs come from `X-Forwarded-For` or `REMOTE_ADDR` and can be spoofed, clients behind one NAT share a limit, and built-in throttles can admit a few extra requests under heavy concurrency; strict guarantees need a custom throttle or an upstream control.
- Cap pagination (`max_limit`). Mechanism: an uncapped limit lets one request pull unbounded rows.

## Next

- Services and selectors the APIs call: [django-services-selectors](../django-services-selectors/SKILL.md)
- Auth endpoints: [django-auth](../django-auth/SKILL.md)
- DRF reference for permissions and throttling: https://www.django-rest-framework.org/api-guide/permissions/ and https://www.django-rest-framework.org/api-guide/throttling/
- Error handler details: the platform plumbing section of your project's `apps/common` (or equivalent) and https://github.com/HackSoftware/Django-Styleguide
