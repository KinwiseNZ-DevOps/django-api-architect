---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code:
```python
# apps/billing/selectors.py
def invoice_get(*, invoice_id):
    return Invoice.objects.get(id=invoice_id)

# apps/billing/apis.py
class InvoiceDetailApi(APIView):
    def get(self, request, invoice_id):
        invoice = invoice_get(invoice_id=invoice_id)
        return Response(InvoiceOutputSerializer(invoice).data)
```
Other endpoints return 404 as {"detail": "Not found."}.

Request: The invoice detail endpoint should raise Http404 from the service when the invoice is missing.
