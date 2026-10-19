---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code:
```python
# apps/billing/selectors.py
def invoice_list_for_user(*, user):
    return Invoice.objects.all()

# apps/billing/apis.py
class InvoiceListApi(APIView):
    def get(self, request):
        rows = invoice_list_for_user(user=request.user)
        return Response(InvoiceOutputSerializer(rows, many=True).data)
```

Request: Filter the invoice list in the API view by checking request.user on each row.
