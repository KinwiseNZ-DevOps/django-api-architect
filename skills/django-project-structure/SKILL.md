---
name: django-project-structure
description: >
  Governs Django app layout, the app pack shape, app manifests, and settings
  organisation for service layer API projects. Use when creating an app or
  feature pack, deciding where code belongs, wiring URLs, or organising
  settings and environment variables. Do not use for the code inside APIs,
  services or tests; those are owned by the sibling specialist skills.
---

# Django Project Structure

Stance: the pack shape and the core-versus-optional split are frozen; file contents belong to the sibling skills. A new domain starts as a pack, never as logic inside the core.

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
3. **Verify.** The app imports, its manifest loads, `INSTALLED_APPS` contains it if and only if it is enabled, and its routes appear under the declared prefix.

## Hard rules

- Every app follows the same file shape: models, selectors, services, apis, tasks, urls, tests. Mechanism: fixed names are the interface; any reader or agent knows where to look without reading the app.
- Core apps stay generic; domain behaviour lives in packs. Mechanism: symptom is core apps growing domain-specific branches; cause is in-place shortcuts; fix is a new pack plus manifest.
- Settings live in one file per environment plus one partial per concern, composed in `base.py`; environment differences are environment variables, not divergent code. Mechanism: duplicated settings drift between environments; builder functions and partials keep single sources.
- Required secrets have no default (fail fast at import); optional values carry safe defaults. Never commit `.env`; ship `.env.example` instead.

## References

Theory source: the public Django Styleguide, https://github.com/HackSoftware/Django-Styleguide (settings and structure sections). Mechanisms above summarise its arguments.

## Next

- Code inside the files: [django-apis-serializers](../django-apis-serializers/SKILL.md), [django-services-selectors](../django-services-selectors/SKILL.md)
- Environment and task wiring: [django-celery](../django-celery/SKILL.md)
