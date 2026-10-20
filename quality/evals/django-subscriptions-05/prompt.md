---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. The Flutter app sells subscriptions through Google Play Billing. Answer from this description and the code below.

apps/billing/apis.py has a MobilePurchaseConfirmApi that receives {'purchase_token': ..., 'product_id': ...} from the Flutter app right after the in_app_purchase plugin reports a successful purchase, and immediately sets the user's subscription to active.

Request: Review this endpoint before we ship it.
