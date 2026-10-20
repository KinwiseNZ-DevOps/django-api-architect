---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/billing/services.py has:
def payment_create(*, order, idempotency_key):
    with transaction.atomic():
        result = payment_provider.create_single_payment(order=order, idempotency_key=idempotency_key)
        Payment.objects.update_or_create(order=order, defaults={'provider_id': result.id, 'status': result.status})
    return result

Request: Review this service before we ship it.
