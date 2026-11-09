---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/accounts/apis.py:
```python
class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
```

Request: We are adding a `stripe_customer_id` and an `internal_risk_score` column to User next week. Anything to check?
