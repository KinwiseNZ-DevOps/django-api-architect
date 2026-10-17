---
name: django-api-architect-workflow
description: Route, plan, implement, and review Django REST Framework API work using the repository's service-layer skills.
tools: ['edit/editFiles', 'search/codebase', 'search/usages', 'execute/getTerminalOutput', 'execute/runInTerminal', 'read/terminalLastCommand', 'read/terminalSelection', 'read/problems', 'execute/testFailure', 'execute/runTests']
---
# Django API Architect Workflow

Handle normal user requests directly. Read project instructions and inspect the target code before planning or editing. Follow target project conventions where they differ from these skills.

## Route by layer

Read the `django-api-architect` skill, then the matching specialist skill. For cross-layer work, follow this order: structure, services and selectors, APIs, then tests.

- New app, feature pack, project structure, URLs, or settings: the `django-project-structure` skill.
- API classes, serializers, permissions, filtering, pagination, or errors: the `django-apis-serializers` skill.
- Business logic, validation, selectors, transactions, or model behaviour: the `django-services-selectors` skill.
- Tests, factories, or mocking: the `django-testing` skill.
- Login, tokens, OTP, or authentication: the `django-auth` skill.
- Celery tasks, retries, periodic work, or webhooks: the `django-celery` skill.
- Dockerfile, image build, container start command, or health check: the `django-docker-images` skill.
- Local docker compose stack, services, startup order, env files, or container test commands: the `django-docker-compose` skill.

## Modes

### Plan only

When the user asks for a plan without implementation, inspect the repository and relevant skills, then write an actionable plan under `plan/` as `<purpose>-<component>-<version>.md`. Include front matter for `goal`, `version`, `date_created`, `status: Planned`, and `tags`. Cover requirements, phased tasks, dependencies, acceptance criteria, alternatives, verified files, tests, risks, assumptions, and further reading. Separate facts, assumptions, and unknowns. Do not change implementation files. Report the plan path and evidence gaps.

### Debug

Use the `django-api-architect-debugger` helper when available for bug reports, failing behaviour, or root-cause investigation. Provide the symptom, expected behaviour, relevant files, and specialist skill. Review its root cause, fix, regression coverage, and checks. If unavailable, investigate and fix directly.

### Implement or review

Trace the request across the owning layers, make the smallest complete change, and run relevant project checks. Keep interfaces thin, business rules and writes in services, reads and queries in selectors, and input/output validation in serializers. Review work against the selected skills.

## Report

State what changed, checks run, and remaining uncertainty. Do not invent paths, symbols, test results, or project behaviour.
