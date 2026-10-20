---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/orders/selectors.py has:
def orders_for_dashboard(*, user):
    return Order.objects.filter(user=user)

apps/orders/apis.py's serializer reads order.user.email and order.billing_profile.plan_name for every order in the list.

Request: The orders dashboard endpoint is slow with more than a handful of orders. Why, and fix the selector.
