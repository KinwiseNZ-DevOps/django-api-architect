---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/services.py:
```python
def trial_is_expired(*, subscription) -> bool:
    return subscription.trial_ends_at < datetime.now()
```

Request: Write tests for trial_is_expired and tell me why the CI run fails only around midnight.
