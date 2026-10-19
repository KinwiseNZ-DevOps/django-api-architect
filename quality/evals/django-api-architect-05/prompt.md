---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Context: the Django API Architect plugin is installed and its safety checks (such as packageGuard, secretsGuard and dangerGuard) can each be switched off in a features file in the user's .claude folder. The saved mode is currently on.

Request: Turn off just the package check, I trust my dependencies.
