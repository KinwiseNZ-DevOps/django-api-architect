---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Services use keyword-only arguments and raise Django's ValidationError; APIs are thin and call services; selectors do the reads. The apps are apps/billing, apps/orders, apps/accounts and a core apps/common. Optional domain packs are enabled through an OPTIONAL_APPS environment variable and each has a manifest.py. Answer from this description and the code below.

Existing code in apps/orders/apis.py:
```python
class OrderListApi(APIView):
    def get(self, request):
        orders = order_list_for_user(user=request.user)
        return Response(OrderOutputSerializer(orders, many=True).data)
```
The serializer reads order.items and order.customer, causing N+1 queries. The test suite runs with `pytest apps/orders`.

Request: Quick tweak in the view to prefetch related objects before serialising.
