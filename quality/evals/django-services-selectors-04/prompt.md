---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

apps/billing/services.py has:
def order_fulfil(*, order):
    with transaction.atomic():
        order.status = 'fulfilled'
        order.save()
        try:
            shipment = Shipment.objects.create(order=order, carrier=order.carrier)
        except IntegrityError:
            logger.warning('shipment create failed for %s', order.id)
        order.notes_create(text='fulfilled')

Request: Review this service for correctness.
