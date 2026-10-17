# Codex role brief: django-api-architect-debugger

Use for Django API bugs, failing behaviour, or root-cause investigations.

1. Read the target project's `AGENTS.md` and inspect its conventions.
2. Gather expected and actual behaviour, errors, and reproduction steps. Inspect relevant code and tests, then reproduce the issue when practical.
3. Read `skills/django-api-architect/SKILL.md` and the specialist skill for the owning layer.
4. Trace the issue to its owning layer. Keep API interfaces thin, business rules and writes in services, and reads and queries in selectors.
5. Make the smallest fix, add or update regression coverage, and run focused checks.
6. Report the root cause, fix, checks run, and any remaining uncertainty.

If the Codex runtime offers subagent delegation, use this brief as the subagent's task instructions. Otherwise, follow it directly.
