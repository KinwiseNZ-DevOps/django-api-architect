---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code:
```python
# apps/orders/services.py
def order_note_add(*, order, text: str):
    order.notes.create(text=text.strip())
```
The project's convention is that every service change ships with tests.

Request: Skip the tests for this service change, it is trivial.
