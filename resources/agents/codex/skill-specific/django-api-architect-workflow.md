# Codex role brief: django-api-architect-workflow

Handle normal user requests directly. Read project instructions and inspect the target code before planning or editing. Follow target project conventions where they differ from these skills.

## Route by layer

Read `skills/django-api-architect/SKILL.md`, then the matching specialist skill. For cross-layer work, follow this order: structure, services and selectors, APIs, then tests.

- New app, feature pack, project structure, URLs, or settings: `skills/django-project-structure/SKILL.md`.
- API classes, serializers, permissions, filtering, pagination, or errors: `skills/django-apis-serializers/SKILL.md`.
- Business logic, validation, selectors, transactions, or model behaviour: `skills/django-services-selectors/SKILL.md`.
- Tests, factories, or mocking: `skills/django-testing/SKILL.md`.
- Login, tokens, OTP, or authentication: `skills/django-auth/SKILL.md`.
- Celery tasks, retries, periodic work, or webhooks: `skills/django-celery/SKILL.md`.

## Modes

### Plan only

If the user requests a plan without implementation, inspect the repository and relevant skills, then write an actionable plan under `plan/` as `<purpose>-<component>-<version>.md`. Include front matter for `goal`, `version`, `date_created`, `status: Planned`, and `tags`. Cover requirements, phased tasks, dependencies, acceptance criteria, alternatives, verified files, tests, risks, assumptions, and further reading. Separate facts, assumptions, and unknowns. Do not change implementation files. Report the plan path and evidence gaps.

### Debug

Use `django-api-architect-debugger` when available for bug reports and root-cause investigation. Give it the symptom, expected behaviour, relevant files, and specialist skill, then review the result. If unavailable, investigate and fix directly.

### Implement or review

Trace the request across the owning layers, make the smallest complete change, and run relevant project checks. Keep interfaces thin, business rules and writes in services, reads and queries in selectors, and validation in serializers. Review work against the selected skills.

## Report

State what changed, checks run, and remaining uncertainty. Do not invent paths, symbols, test results, or project behaviour.
