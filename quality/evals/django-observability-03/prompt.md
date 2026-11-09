---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/common/apis.py:
```python
class HealthApi(APIView):
    permission_classes = []
    def get(self, request):
        connection.ensure_connection()
        return Response({'ok': True})
```
The load balancer uses this path as its liveness check.

Request: The database restarted for ten seconds and the platform restarted every web instance. Why, and what should change?
