# Changelog

All notable changes to this plugin are listed here, newest first. To cut a release, add your notes under "Unreleased", then run `python scripts/bump_version.py patch` (or `minor` or `major`). It updates the plugin version and moves those notes under the new version.

## [Unreleased]

- Added triggering tests (`evals/triggers.jsonl`): every skill has an obvious, a paraphrase and an unrelated query, checked by the validator and exported as `tool_used` graders.
- The always-on rules now default to `auto`, so they load only in Django projects (`manage.py`, or Django in the requirements).
- Moved Hard rules to the top of every skill, above the gate.

## [0.7.1] - 2026-10-23

- Added the rule to trust the user's description of their own system: check the real files, report facts only, and never argue then concede. It is in the always-on rules, the router hard rules, AGENTS.md and the agent profiles.

## [0.7.0] - 2026-10-23

- Added `django-aws-deployment`: choosing between ECS on Fargate, App Runner and Elastic Beanstalk, shared production settings, health checks behind a load balancer, secrets, migrations and logging, from AWS documentation and the App Runner blog post.

## [0.6.0] - 2026-10-21

- Added django-subscriptions: plan/lifecycle management, webhook-verified state changes, soft cancellation with history, and dunning, generalised from a real sample PayPal subscription implementation's mistakes (client-trusted activation, unconditional deletion on cancel, immediate cancellation on first payment failure), verified live against that sample app. Also covers Apple App Store Server Notifications and Google Play real-time developer notifications for in-app subscriptions.

## [0.5.1] - 2026-10-21

- Added transaction correctness guidance to django-services-selectors: the poisoned-transaction trap, savepoint nesting, on_commit with savepoints, model state after rollback, ATOMIC_REQUESTS scope, and never holding a transaction open across an external call.
- Added query-pattern guidance to django-services-selectors: evaluating a queryset once, select_related/prefetch_related, defer/only, bulk methods skipping signals, raw SQL parameterization, and search.

## [0.5.0] - 2026-10-20

- Added django-open-banking: BlinkPay payment initiation (PayNow, AutoPay) and account data access (Blink Data), behind a provider-agnostic interface.

## [0.4.0] - unreleased

- Initial skills.
