---
name: django-project-structure
description: >
  Use when creating an app or feature pack, deciding where code or a setting or
  an API key belongs, wiring URLs, or organising settings and environment
  variables, including when asked to put domain logic in a core app. Governs
  Django app layout, the app pack shape, app manifests, and settings
  organisation for service layer API projects. Do not use for the code inside
  APIs, services or tests; those are owned by the sibling specialist skills.
---

# Django Project Structure

Stance: the pack shape and the core-versus-optional split are frozen; file contents belong to the sibling skills. A new domain starts as a pack, never as logic inside the core.

## Hard rules

- Every app follows the same file shape: models, selectors, services, apis, tasks, urls, tests. Mechanism: fixed names are the interface; any reader or agent knows where to look without reading the app.
- Core apps stay generic; domain behaviour lives in packs. Mechanism: symptom is core apps growing domain-specific branches; cause is in-place shortcuts; fix is a new pack plus manifest.
- Settings live in one file per environment plus one partial per concern, composed in `base.py`; environment differences are environment variables, not divergent code. Mechanism: duplicated settings drift between environments; builder functions and partials keep single sources.
- Required secrets have no default (fail fast at import); optional values carry safe defaults. Never commit `.env`; ship `.env.example` instead.
- Never edit a migration that has already been applied in another environment. Mechanism: symptom is a schema that no longer matches any migration and cannot be replayed; cause is editing history that other environments have already recorded; fix is a new corrective migration, never a rewrite of an old one.
- Apps call each other through services and selectors, never by importing another app's models or private modules; use signals or tasks for events one app should not know about another. Mechanism: symptom is circular imports and a schema change that breaks unrelated apps; cause is models imported across app boundaries; fix is one narrow call surface per app.
- A shared `common` app is imported by other apps and imports none of them. Mechanism: a base layer that imports upward creates import cycles.
- Production settings are explicit: `SECRET_KEY` from the environment, `DEBUG` off, and `ALLOWED_HOSTS` and CORS origins as named lists, never wildcards. Mechanism: debug pages leak settings, and a wildcard widens who may call the API from a browser.
- Production serves HTTPS only: `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` on, `SECURE_SSL_REDIRECT` on unless the load balancer already redirects, and `SECURE_HSTS_SECONDS` set (start with a short value, because browsers remember it). Behind a proxy also set `SECURE_PROXY_SSL_HEADER`, or the redirect loops. Mechanism: a cookie sent over plain HTTP can be read on the network; `python manage.py check --deploy` lists each missing setting.
- Act only on what the user asked. Before answering or changing anything, open the relevant files and check what is already done; report only what you checked, never guess, and do not redo finished work. Reason: guesses and repeated work waste the user's credit.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| Question is which file or app a change belongs in | Continue |
| Someone wants to add logic to a shared core app for one domain | Push back; make a pack |
| Project has no app structure yet (greenfield) | Continue; establish the pack shape from the start |

## Steps

1. **Detect.** List the apps under `apps/` (or the project's equivalent) and the settings layout under `config/settings/`. Check whether each app has the standard shape: `models.py`, `selectors.py`, `services.py`, `apis.py`, `tasks.py`, `urls.py`, `tests/`.
2. **Fix.** For a new domain feature: copy the pack skeleton into `apps/<name>/`, fill the standard files, and register it. Registration has two parts, both required:
   - Add the app module to the optional (or core) app list, and enable it through the environment variable that controls optional apps (a comma-separated list, so no code change is needed to switch a pack on or off).
   - Give the app a `manifest.py` declaring `APP_MANIFEST` with all seven keys: `app`, `name`, `optional`, `dependencies`, `required_settings`, `url_prefix`, `urlconf`. The loader validates the keys and the app label match, so a wrong manifest fails loudly at import.
   - URL mounting is dynamic: the root URL config mounts a pack's `urlconf` under its `url_prefix` only when the app is installed, so disabling a pack removes its routes with it.
   - Migrations travel with the change that caused them. Generate the app's initial migration with `makemigrations`, read the generated file, and commit it with the app. A model without its migration is not installable.
   - Module size: when one file passes roughly 500 lines (a rule of thumb, not a Django rule), turn it into a package of the same name, split by topic, and re-export from `__init__.py` so existing imports keep working.
   - Browser clients on another origin need CORS, which is separate from CSRF and which Django does not provide. With `django-cors-headers` (ask before adding a dependency): add `corsheaders` to the installed apps, put `corsheaders.middleware.CorsMiddleware` high in `MIDDLEWARE` and before `CommonMiddleware` (the package documents this order), and read `CORS_ALLOWED_ORIGINS` from an environment list. Mobile-only APIs do not need it.
3. **Verify.** The app imports, its manifest loads, `INSTALLED_APPS` contains it if and only if it is enabled, its routes appear under the declared prefix, and `migrate` runs clean against the committed migrations.

## References

Theory source: the public Django Styleguide, https://github.com/HackSoftware/Django-Styleguide (settings and structure sections). Mechanisms above summarise its arguments.

## Next

- Code inside the files: [django-apis-serializers](../django-apis-serializers/SKILL.md), [django-services-selectors](../django-services-selectors/SKILL.md)
- Environment and task wiring: [django-celery](../django-celery/SKILL.md)
- Running the project in containers: [django-docker-images](../django-docker-images/SKILL.md), [django-docker-compose](../django-docker-compose/SKILL.md)
