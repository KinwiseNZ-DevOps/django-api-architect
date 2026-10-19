---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Services use keyword-only arguments and raise ValidationError; APIs are thin and call services. The apps are apps/billing and apps/accounts. Answer from this description and the code below.

Existing code in apps/accounts/services.py:
```python
@transaction.atomic
def user_create(*, email: str, password: str) -> User:
    user = User.objects.create_user(email=email, password=password)
    return user
```
apps/accounts/tasks.py already has `welcome_email_task(user_id)` decorated with @shared_task.

Request: Send the welcome email at the end of the user_create service, which runs in a transaction.
