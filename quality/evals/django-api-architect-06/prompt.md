---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a small Django project with a single app called notes_app (models.py with Note, views.py with a few function views, urls.py). There is no apps/common, no manifest files and no settings package, just settings.py. pytest is not installed.

Request: Add a notes endpoint to this small Django project. It has no apps/common, no manifest files and no settings package.
