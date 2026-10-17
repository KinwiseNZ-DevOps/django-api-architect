---
name: django-api-architect
description: >
  Router and shared guardrails for Django REST Framework API projects built on
  a service layer architecture with thin APIs, services, selectors and app
  packs. Use when a task touches a Django or DRF backend, when it is unclear
  which specialist skill applies, or when starting any Django API change. Do
  not use for Flutter or frontend work, deployment platforms, or non-Django
  backends.
---

# Django API Architect (router)

Stance: the architecture is frozen (thin interfaces, business logic in services and selectors), the implementation inside those boxes is flexible. This skill routes to the right specialist and enforces the guardrails every change must satisfy.

## Gate

Route by the layer the task actually touches. When in doubt, ask which file the change belongs in; the app pack shape decides that.

| Situation | Action |
|---|---|
| Task spans several layers (new feature end to end) | Start at django-project-structure, then route per layer |
| Where business logic lives, app layout, settings | [django-project-structure](../django-project-structure/SKILL.md) |
| Writing or changing API classes, serializers, filters, pagination, error shape | [django-apis-serializers](../django-apis-serializers/SKILL.md) |
| Writing or changing services, selectors, validation, transactions | [django-services-selectors](../django-services-selectors/SKILL.md) |
| Writing or changing tests, mocking, factories | [django-testing](../django-testing/SKILL.md) |
| Login, tokens, OTP, authentication wiring | [django-auth](../django-auth/SKILL.md) |
| Celery tasks, retries, periodic tasks, webhook dispatch | [django-celery](../django-celery/SKILL.md) |

## Agent selection

When this skill or one of its sibling skills is invoked, inspect the agents available to the current runtime. In this repository, use the host profile when available: GitHub Copilot profiles are in `.github/agents/`, Claude Code profiles are in `.claude/agents/`, and Codex role briefs are in `agents/codex/`. Their names use the `django-api-architect-` prefix to reduce clashes with agents from other skills. Choose `django-api-architect-debugger` for a reported bug, failing behaviour, or root-cause investigation. Choose `django-api-architect-implementation-planner` when the user requests a plan without implementation. Give it the request and relevant skills, then review its plan. Choose `django-api-architect-implementer` for API design, implementation, review, or other skill work. Give the selected agent the user's request and the matching skill instructions, then have it carry the work through the workflow in its profile. Review the result against the relevant skill's hard rules before reporting back.

Use this delegation when the runtime can start or hand off to an available agent. Codex runtimes without project agent profiles should read the matching role brief and use native subagent delegation when available. If no matching agent is discoverable or the runtime cannot invoke one, carry out the same workflow directly with the routed skill. Do not stop to ask the user to choose an agent.

## Steps

1. **Select an agent.** Apply the agent selection rules above. If the runtime cannot delegate, continue the same workflow directly.
2. **Detect.** Identify the layer: an interface (API, task, command), the core (services, selectors, models), or structure (apps, settings). Locate the target file using the pack shape: every app has `models.py`, `selectors.py`, `services.py`, `apis.py`, `tasks.py`, `urls.py`, `tests/`.
3. **Route.** Give the selected agent the matching specialist skill and follow its workflow. If the change spans several layers, work in dependency order: structure, then services and selectors, then APIs, then tests.
4. **Verify.** Apply the shared hard rules below, then the routed skill's own verification. Review delegated work before returning the result.

## Hard rules

- Business logic never goes in APIs, views, serializers, forms, model `save`, custom managers or signals. Mechanism: symptom is logic that cannot be traced or tested in one place; cause is logic scattered across interface layers; fix is a service or selector with keyword-only arguments.
- Interfaces (APIs, tasks) validate input and call services; they contain no business logic. Mechanism: duplicated or divergent behaviour across interfaces; fixed by keeping one service as the single implementation.
- Read the target project's own conventions before changing it; these skills describe the default architecture, and the project in front of you wins where they differ. Mechanism: blind application of defaults creates drift inside an existing codebase.
- Make the smallest correct change and verify it with the project's own test suite. Mechanism: unverified refactors are the main way service layer projects regress.

## Next

All specialist skills are linked in the gate table above.
