# Changelog

All notable changes to this plugin are listed here, newest first. To cut a release, add your notes under "Unreleased", then run `python scripts/bump_version.py patch` (or `minor` or `major`). It updates the plugin version and moves those notes under the new version.

## [Unreleased]

## [0.10.1] - 2026-11-07

- Added kinwise-analytics to the Works with other repos table: analytics depends on this repo for any new selector, endpoint or export.

## [0.10.0] - 2026-11-05

- Added a Works with other repos section to the router skill and README: it names the repos this one depends on or is relied on by, and when to hand off. Marketing comes first in the decision order (marketing, then look and feel, then the technical work). The map is in skills-repos-dependency-map.md beside the repos.

## [0.9.0] - 2026-10-29

- Added the rule to act only when told and to analyse the repo before answering: no guesswork, no redoing finished work, and show the real artifact when asking the user to review or approve. It is in AGENTS.md and as a hard-rule bullet in every skill.

## [0.8.0] - 2026-10-26

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
