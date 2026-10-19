---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Services use keyword-only arguments and raise Django's ValidationError; APIs are thin and call services; selectors do the reads. The apps are apps/billing, apps/orders, apps/accounts and a core apps/common. Optional domain packs are enabled through an OPTIONAL_APPS environment variable and each has a manifest.py. Answer from this description and the code below.

Existing code:
```python
# apps/billing/apis.py
class StripeWebhookApi(APIView):
    authentication_classes = []
    def post(self, request):
        event = stripe.Webhook.construct_event(request.body, request.headers['Stripe-Signature'], settings.STRIPE_WEBHOOK_SECRET)
        handle_event(event)
        return Response(status=200)
```

Request: Process the Stripe webhook synchronously in the view so events are handled immediately.
