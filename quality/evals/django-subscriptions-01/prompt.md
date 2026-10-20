---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/billing/views.py has: def paypal_return(request, subscription_id, plan): Subscription.objects.create(user=request.user, plan=plan, status='active'); return redirect('dashboard')

Request: Finish wiring up the subscription checkout return page.
