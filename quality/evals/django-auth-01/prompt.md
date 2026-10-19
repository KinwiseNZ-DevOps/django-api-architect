---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Services use keyword-only arguments and raise Django's ValidationError; APIs are thin and call services; selectors do the reads. The apps are apps/billing, apps/orders, apps/accounts and a core apps/common. Optional domain packs are enabled through an OPTIONAL_APPS environment variable and each has a manifest.py. Answer from this description and the code below.

Existing code:
```python
# apps/accounts/apis.py
class LoginApi(TokenObtainPairView):
    throttle_scope = 'auth'
```
The project uses djangorestframework-simplejwt. apps/accounts/services.py has `login_ip_record(*, user, ip)`.

Request: Alert users by email when they log in from a new IP address.
