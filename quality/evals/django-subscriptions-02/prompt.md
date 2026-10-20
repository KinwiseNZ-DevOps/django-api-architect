---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/billing/services.py has:
def subscription_cancel(*, subscription_id):
    cancel_with_provider(subscription_id)
    Subscription.objects.get(provider_subscription_id=subscription_id).delete()

Request: Review this cancellation service.
