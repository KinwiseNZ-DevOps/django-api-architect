---
name: django-api-architect
description: >
  Router and shared guardrails for Django REST Framework API projects built on a
  service layer architecture with thin APIs, services, selectors and app packs.
  Use when answering or writing any Django or DRF backend change, including
  small ones such as a new endpoint, a serializer tweak, a view optimisation, an
  export, or a request to switch these rules off, and when it is unclear which
  specialist skill applies. Do not use for Flutter or frontend work, deployment
  platforms other than AWS, or non-Django backends.
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
| Dockerfile, image build, container start command, health check | [django-docker-images](../django-docker-images/SKILL.md) |
| Local docker compose stack: web, database, broker, workers, env files, container test commands | [django-docker-compose](../django-docker-compose/SKILL.md) |
| Deploying to AWS: Fargate, App Runner or Elastic Beanstalk, production settings, health checks, migrations on release | [django-aws-deployment](../django-aws-deployment/SKILL.md) |
| Open banking payment initiation or bank account data access (BlinkPay or another provider) | [django-open-banking](../django-open-banking/SKILL.md) |
| Subscription plans, activation, cancellation, upgrades/downgrades, billing webhooks | [django-subscriptions](../django-subscriptions/SKILL.md) |

## Agent selection

When this skill or one of its sibling skills is invoked, use the `django-api-architect-workflow` profile when available. It handles normal requests and has plan-only, debug, implementation, and review modes. For reported defects, it may use the optional `django-api-architect-debugger` helper. Names use the `django-api-architect-` prefix to reduce clashes with agents from other skills. Give the workflow the user's request and relevant specialist skill instructions, then review its work against those skills' hard rules. If no profile or delegation is available, carry out the same workflow directly. Do not stop to ask the user to choose an agent.

Use this delegation when the runtime can start or hand off to an available agent. Codex runtimes without project agent profiles should read the matching role brief and use native subagent delegation when available. If no matching agent is discoverable or the runtime cannot invoke one, carry out the same workflow directly with the routed skill. Do not stop to ask the user to choose an agent.

## Steps

1. **Select a workflow.** Apply the agent selection rules above. If the runtime cannot delegate, continue the same workflow directly.
2. **Detect.** Identify the layer: an interface (API, task, command), the core (services, selectors, models), or structure (apps, settings). Locate the target file using the pack shape: every app has `models.py`, `selectors.py`, `services.py`, `apis.py`, `tasks.py`, `urls.py`, `tests/`.
3. **Route.** Give the workflow the matching specialist skill and follow its workflow. If the change spans several layers, work in dependency order: structure, then services and selectors, then APIs, then tests.
4. **Verify.** Apply the shared hard rules below, then the routed skill's own verification. Review delegated work before returning the result.

## When the project does not have the shape yet

These skills assume a shared package for the error handler and pagination, app manifests, a settings package, drf-spectacular and pytest configured. Check for each before relying on it. If one is missing, say so in one line and follow the project's own way of doing that job; add the missing piece only when the task needs it, keep it minimal, and ask first when it needs a new dependency. Mechanism: copying the default structure into a project that does not have it creates a second, half-used convention that nothing else follows.

## Hard rules

- Business logic never goes in APIs, views, serializers, forms, model `save`, custom managers or signals. Mechanism: symptom is logic that cannot be traced or tested in one place; cause is logic scattered across interface layers; fix is a service or selector with keyword-only arguments.
- Interfaces (APIs, tasks) validate input and call services; they contain no business logic. Mechanism: duplicated or divergent behaviour across interfaces; fixed by keeping one service as the single implementation.
- Read the target project's own conventions before changing it; these skills describe the default architecture, and the project in front of you wins where they differ. Mechanism: blind application of defaults creates drift inside an existing codebase.
- Make the smallest correct change and verify it with the project's own test suite. Mechanism: unverified refactors are the main way service layer projects regress.

## Next

All specialist skills are linked in the gate table above.

## Always-on mode

When the plugin is installed, a start-up hook adds [always-on-rules.md](references/always-on-rules.md) to every Claude Code session. The user can say "stop django mode" to pause it, or ask for the saved mode to be set to on, off or auto. The rules file is the single source of those rules; edit it, not a copy. The same hooks also run safety checks (risky commands, secrets, invented packages, licences, risky code patterns, suspicious pasted prompts, and a reminder when code changed but no checks ran). Each can be switched off in the features file described in the README, and none edits a file on its own.
