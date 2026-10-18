---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Pass our SECRET_KEY and database password as ARG values in the Dockerfile so the build can run collectstatic.
