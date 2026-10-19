---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/orders/apis.py:
```python
class OrderListApi(APIView):
    def get(self, request):
        orders = order_list_for_user(user=request.user)
        return Response(OrderOutputSerializer(orders, many=True).data)
```
The serializer reads order.items and order.customer, causing N+1 queries. The test suite runs with `pytest apps/orders`.

Request: Quick tweak in the view to prefetch related objects before serialising.
