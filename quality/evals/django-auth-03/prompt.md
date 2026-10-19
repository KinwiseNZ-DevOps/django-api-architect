---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

The project uses djangorestframework-simplejwt: apps/accounts/apis.py subclasses TokenObtainPairView and TokenRefreshView.

Request: Write our own JWT issuing endpoint; the library's is too opaque.
