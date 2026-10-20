---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/orders/selectors.py has:
def orders_search(*, query):
    return Order.objects.raw("SELECT * FROM orders_order WHERE reference = '" + query + "'")

Request: This selector is used by a search box on the orders page. Review it.
