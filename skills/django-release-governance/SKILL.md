---
name: django-release-governance
description: >
  Use when setting up or changing branch protection, pull request rules, commit
  message rules, git hooks, a CI workflow, a release or version tag, a hotfix, a
  rollback, a feature flag or kill switch, or an incident review for a Django
  API, including when asked to push straight to the main branch, force-push, or
  fix forward in production. Governs how Django API changes are reviewed, tested,
  released, switched on and rolled back. Do not use for the test code itself
  (django-testing), the AWS hosting setup (django-aws-deployment) or logging and
  alerts (django-observability).
---

# Django Release Governance

Stance: every change reaches production the same way: reviewed, tested by CI, tagged, deployable and reversible. The branching model and the CI vendor are flexible; the controls below are frozen.

## Hard rules

- Nobody pushes to the default branch; every change arrives by pull request with passing checks. Mechanism: a direct push skips review and CI, and the history cannot be trusted afterwards; fix is a branch protection rule or ruleset that also applies to admins.
- Never rewrite published history: no force-push to a shared branch, and undo with `git revert`. Mechanism: rewriting changes commits other people have already built on, so their copies diverge and the audit trail is lost. Ask first before any force-push to a branch that exists on a remote.
- CI is the authority; local hooks are a convenience. Mechanism: hooks can be skipped or never installed, so every check a hook runs (format, lint, tests, secret scan, commit message) also runs in CI.
- In an incident, revert first and fix second. Mechanism: symptom is a long outage while someone hunts a clever fix; cause is trusting a quick change under pressure; fix is to restore the last known good release, then find the cause calmly. If a revert is impossible, branch from the released tag and ship only the fix.
- A change that touches the database must work with the previous release as well as the new one. Mechanism: a rollback runs old code against the new schema; fix is to add first, switch the code, and remove old columns in a later release (expand, then contract).
- Every release is an immutable tag with release notes, and what runs in production is a tag, not a branch tip. Mechanism: without a tag nobody can say which code is live, and a rollback has no target.
- Risky or externally dependent behaviour ships behind a flag that defaults to the safe state, is read through one function, and is removed once the rollout is finished. A flag is a release control, never an authorisation check. Mechanism: a flag lets a person switch a feature off in seconds without a deploy; a forgotten flag becomes untested code paths.
- Third-party CI actions are pinned to a full commit hash, workflows declare the least `permissions` they need, and no secret is printed or passed to code from a fork. Mechanism: an action or token with wide rights is a way into the repository.
- Act only on what the user asked. Before answering or changing anything, open the relevant files and check what is already done; report only what you checked, never guess, and do not redo finished work. Reason: guesses and repeated work waste the user's credit.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| Branch rules, pull request rules, hooks, CI, tags, hotfix, flag or incident review | Continue |
| Someone asks to push straight to the default branch or force-push a shared branch | Push back; open a pull request, or revert |
| Production is broken now and a recent release is the likely cause | Revert to the last good tag first |
| Writing the tests or the AWS deploy config | Use [django-testing](../django-testing/SKILL.md) or [django-aws-deployment](../django-aws-deployment/SKILL.md) |

## Steps

1. **Detect.** Read the CI workflow files, branch protection settings if visible, any hook config, the tags and release notes, the commit history style, and how flags are read. Say what you could not see, such as repository settings that need a person with access.
2. **Fix.** Least invasive first:
   - Pull requests: describe what changed, how, and why; keep a change to roughly 300 to 500 changed lines (a rule of thumb) by stacking small branches onto one feature branch; review only when tests pass and debug code is gone. Reviewers read the tests and ask about security, in a respectful and explained way.
   - Commits: one agreed format such as Conventional Commits (`type(scope): description`), checked in CI, with the issue id where one exists.
   - CI job: install from the pinned requirements, start the same database engine and cache as production as service containers with health checks, run migrations, run `makemigrations --check --dry-run` to catch a missing migration, run the tests with a coverage floor, lint, scan for secrets, and run `python manage.py check --deploy` with production settings. Cache dependencies. Run the same job on every push to a pull request.
   - Dependencies and secrets: turn on automatic dependency update pull requests and secret scanning, and require 2FA for everyone with write access. Use code owners so sensitive paths (auth, payments, migrations) need a named reviewer.
   - Releases: semantic version tags (`major.minor.patch`), release notes built from merged pull requests, deploy the tag. The change log in this repository's own CHANGELOG is the model.
   - Flags: store them in a small table or a flag service, read them through one selector function with a short cache, default to off or the safe state, record who changed a flag and when, and delete the flag after rollout.
   - Incidents: say so and acknowledge first; find the cause with data (error tracker, logs, metrics) before acting; revert; watch the system for a few hours; then hold a blameless review that names causes in the system, not people, and lists actions with owners and dates. An incident is closed when the actions are done.
3. **Verify.** A test pull request is blocked until checks pass; CI fails on a deliberately broken test and a missing migration; the last tag can be redeployed. Say which settings and workflows you could not run or see.

## Next

- Test code and what to mock: [django-testing](../django-testing/SKILL.md)
- Logs, error tracking, health checks and alerts: [django-observability](../django-observability/SKILL.md)
- Migrations on release and AWS roles for CI: [django-aws-deployment](../django-aws-deployment/SKILL.md)
- Tasks that must survive a rollback: [django-celery](../django-celery/SKILL.md)
