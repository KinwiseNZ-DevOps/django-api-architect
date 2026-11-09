---
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Project context (nothing else is available to read): a Django REST Framework API called shop-api with the apps apps/billing, apps/orders, apps/accounts and a core apps/common. Each app has models.py, selectors.py, services.py, apis.py, tasks.py, urls.py and tests/. Answer from this description and the code below.

Existing code in apps/billing/apis.py:
```python
class InvoiceApi(APIView):
    def get(self, request, pk):
        try:
            return Response(InvoiceSerializer(invoice_get(pk=pk)).data)
        except Exception:
            return Response({'detail': 'Something went wrong'}, status=400)
```

Request: Make errors in production visible to the team without anyone reading log files.
