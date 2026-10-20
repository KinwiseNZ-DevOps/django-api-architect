---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/billing/urls.py has: path('create-subscription/<subID>/<plan>', views.create_subscription). apps/billing/views.py has: def create_subscription(request, subID, plan): Subscription.objects.create(user=request.user, provider_subscription_id=subID, plan=plan, status='active'); return redirect('dashboard')

There is no call anywhere in the billing app to the payment provider's API, and no webhook endpoint exists. A tester reports that visiting /billing/create-subscription/anything123/Premium while logged in grants an active Premium subscription with no payment made.
