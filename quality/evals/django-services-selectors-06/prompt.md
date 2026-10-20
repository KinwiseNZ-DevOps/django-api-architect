---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/orders/signals.py has a post_save receiver on Order that sends an invoice email. apps/billing/services.py has:
def cancel_overdue_orders():
    Order.objects.filter(status='pending', due_date__lt=timezone.now()).update(status='cancelled')

Request: We noticed customers aren't getting a cancellation email when their order is auto-cancelled by this job. Why not, and fix it.
