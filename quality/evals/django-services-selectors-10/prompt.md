---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/accounts/receivers.py:
```python
@receiver(post_save, sender=User)
def send_welcome(sender, instance, created, **kwargs):
    if created:
        welcome_email_task.delay(instance.id)
```
The receiver module is never imported anywhere, so no email goes out.

Request: Make the welcome email work.
