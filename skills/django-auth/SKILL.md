---
name: django-auth
description: >
  Use when building or changing login, tokens, simplejwt, OTP codes and how they
  are stored, new-IP or login alerts, or login throttling, including when asked
  to write a custom token endpoint or to store codes in plaintext. Governs
  authentication in Django API projects: JWT login, refresh and logout,
  passwordless OTP codes, admin second factor, and login throttling. Do not use
  for general API permissions or throttle scopes outside auth (django-apis-
  serializers).
---

# Django Authentication

Stance: JWT via `rest_framework_simplejwt` is the primary flow for SPA clients; OTP codes are the passwordless flow; the admin carries its own OTP second factor. Library views are wrapped, never reimplemented.

## Hard rules

- Wrap library auth views; add behaviour via serializer subclasses and view subclasses. Mechanism: hand-rolled token logic drifts from library security fixes; wrapping keeps upgrades safe.
- Never store OTP codes in plaintext, and always consume them on use or on failed match. Mechanism: symptom is replayable or brute-forceable codes; cause is persistent plaintext codes; fix is hashed, TTL-bound, single-use storage with constant-time comparison.
- A failed login must never trigger side effects such as new-IP alerts or recording the IP on the user. Mechanism: symptom is attacker-supplied data stored on a real user's record, or alerts for attempts that never authenticated; cause is running the side effect before the credentials are verified; fix is hooking after `super().validate(attrs)` succeeds. Security logging of failed attempts is separate and allowed.
- Login gets its own stricter anonymous throttle, separate from general API scopes. Mechanism: credential stuffing otherwise borrows the whole API's rate budget.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| Login, refresh, logout, OTP, or admin auth changes | Continue |
| Someone wants to reimplement token issuing by hand | Push back; wrap the library |
| Authorization (who may call which endpoint) rather than authentication | Route to django-apis-serializers for permission classes |

## Steps

1. **Detect.** Locate `auth_urls.py` and the auth API module in the users app. Confirm the shape: obtain-pair, refresh and blacklist endpoints wrapping `simplejwt` views; rotated refresh tokens; logout returning 205 and blacklisting the refresh token; a dedicated stricter throttle scope on login only.
2. **Fix.**
   - To add post-login behaviour, subclass the obtain-pair serializer and hook after `super().validate(attrs)`, so failed logins never trigger it. Example in house code: recording the login IP and alerting when it is new.
   - For OTP: generate with `secrets`; store only the SHA-256 hash in the cache (Redis), keyed by lowercased email, with a TTL from settings; verify with `secrets.compare_digest`; consume on success and on mismatch, so every attempt is single-use; run the cheap format check before touching the cache. Errors form a small hierarchy (`OtpError`, `OtpExpiredError`, `OtpInvalidError`).
   - Send OTP email through a Celery task with bounded retries; keep `OTP_SHOW_CODE_IN_UI` off in production.
   - Document auth endpoints in the OpenAPI schema with their failure codes: 401 invalid credentials, 400 blacklisted token, 429 throttled.
3. **Verify.** Tests cover: successful login issues both tokens, wrong password does not record IP data, refresh rotates and old refresh tokens are blacklisted, OTP single-use semantics, and login throttle engagement.

## References

Theory source: the public Django Styleguide, https://github.com/HackSoftware/Django-Styleguide (authentication sections, including a session cookie alternative for same-domain frontends).

## Next

- Task retry mechanics for OTP email: [django-celery](../django-celery/SKILL.md)
- API documentation annotations: [django-apis-serializers](../django-apis-serializers/SKILL.md)
