---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/apis.py:
```python
class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    coupon_code = serializers.CharField(required=False)

    def validate(self, attrs):
        return attrs

class CheckoutApi(APIView):
    def post(self, request):
        s = CheckoutSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        order = checkout_create(user=request.user, **s.validated_data)
        return Response({'total': str(order.total)})
```

Request: Add a discount calculation to the checkout serializer's validate() method so the API returns the discounted total.
