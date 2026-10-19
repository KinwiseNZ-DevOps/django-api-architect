---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django project with apps/orders/services.py containing `def order_cancel(*, order)` that raises ValidationError for shipped orders and otherwise sets status to cancelled. The project has no pytest.ini, no conftest.py, and pytest and pytest-django are not in requirements.

Request: Write tests for this service. The project has no pytest.ini or conftest.py.
