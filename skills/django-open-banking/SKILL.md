---
name: django-open-banking
description: >
  Governs open banking integrations in Django API projects: initiating
  account-to-account payments and reading bank account data (balances,
  transactions) through a provider such as BlinkPay, behind a
  provider-agnostic interface so a second country or provider can be
  added without rewriting callers. Use when building or changing a
  payment consent, a bank data consent, a payment or consent status
  check, a refund, or an open banking provider adapter. Do not use for
  card-only payment gateways with no bank consent step, for the service
  and selector conventions themselves (django-services-selectors), or
  for task retry mechanics in general (django-celery).
---

# Django Open Banking

Stance: the provider interface and the rule that nothing here is ever trusted from the client are frozen; the specific provider, and which of its flows a project uses, are flexible. A provider-only integration (payments, or data, or both) is normal; implement only the interface the project actually needs.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| Initiating or checking a payment, or a refund | Continue; see [provider-interface.md](references/provider-interface.md) and the provider's payments reference |
| Reading account, balance or transaction data | Continue; see [provider-interface.md](references/provider-interface.md) and the provider's data reference |
| Adding a second provider or country | Write a new adapter against the existing interface; do not change callers or add provider-specific branches outside the adapter |
| A redirect, callback or webhook-shaped ping arrived | Treat it only as a signal to re-fetch status from the provider's API; never as the outcome itself |
| The task is card-only, with no bank consent or redirect step | This skill does not apply; treat it as a normal third-party API integration |

## Steps

1. **Detect.** Find the existing provider interface and adapter (an `open_banking` app, or wherever the project keeps third-party payment and data integrations). Confirm which products are in use: payment initiation, data access, or both, and which provider backs each.
2. **Fix or build.**
   - Define or extend the interface in service terms (`initiate_payment`, `get_payment_status`, `list_accounts`, ...), never in the provider's own request and response shapes; a caller must not need to know which provider is behind the interface.
   - Put provider calls in a service (a class-based service is the expected exception here, per django-services-selectors, since one provider adapter is a cohesive multi-method unit). Never call a provider's API from an API class, a serializer, a task body or a view.
   - Store provider-issued identifiers (consent ID, payment ID, refund ID) on your own models and upsert with `update_or_create` keyed on that ID, the same pattern as any third-party upsert (django-services-selectors).
   - Amount, currency, payment reference and requested data permissions are decided server-side from your own order, subscription or consent record, never accepted from the client, the return URL or any request the customer's browser can shape.
   - Poll status with a bounded Celery task (django-celery): short, frequent polls while a consent is awaiting authorisation, then back off; never poll indefinitely, and never trust a redirect or callback payload over a fresh server-side status read.
3. **Verify.** Tests cover: a server-decided amount survives a client attempt to override it, an idempotent retry does not duplicate a payment or refund, a redirect with no recognised status is not treated as success, and a second provider's adapter satisfies the same interface tests as the first (see django-testing).

## Hard rules

- Never trust a payment or consent outcome from a redirect, return URL or callback. Mechanism: the only trustworthy source is your own server calling the provider's status endpoint with your credentials; browser-side parameters can be replayed, guessed or simply never arrive. Fix: on any return, re-fetch status server-side before acting, and branch on a typed status field, never on a human-readable message.
- Amount, currency, PCR-style payment reference and requested permissions come from your own records, never from the client. Mechanism: a client-supplied amount or permission list is a direct path to paying the wrong amount or over-sharing data. Fix: the service that creates a consent computes these from the order, subscription or consent record it is given, not from the request body.
- Every write to a provider (create a consent, a payment or a refund) carries an idempotency key, generated once per distinct business action and reused verbatim on every retry of that same action. Mechanism: a provider API processes a repeated key as a no-op or returns the original result; a fresh key on retry risks a duplicate payment. Fix: generate the key when the business action starts, store it alongside the local record, and pass the stored value on every retry, never a new one.
- A provider's own "complete" or "consumed" status does not mean money moved or data is available; read the dedicated settlement or completion field the provider defines for that fact. Mechanism: providers model the consent and the underlying payment as separate objects with separate terminal states, and conflating them is a direct path to shipping an order that was never paid. Fix: name the one field each provider adapter must expose as "did this actually settle", and never substitute the consent or request status for it.
- Provider credentials and access tokens stay server-side, cached and reused until shortly before expiry, never requested per call and never reachable from a browser or mobile client. Mechanism: a token or secret shipped to a client can be extracted from it. Fix: the adapter's token handling is the only code that touches credentials, and the rest of the codebase only ever sees the typed interface.
- A new provider is a new adapter implementing the existing interface, not a provider-specific branch added to callers or to the interface itself. Mechanism: branching call sites on which provider is active is how a provider-agnostic design quietly stops being one. Fix: if the interface cannot express what the new provider needs, extend the interface itself and update every adapter, rather than special-casing one caller.

## References

- [provider-interface.md](references/provider-interface.md): the provider-agnostic interface shape, where the adapter lives in the app pack, and how a second provider plugs in.
- [blinkpay-payments.md](references/blinkpay-payments.md): BlinkPay's Blink Payments product (PayNow single payments, AutoPay recurring payments, refunds), condensed: consent types, flow choice, lifecycle states, idempotency and error codes.
- [blinkpay-data.md](references/blinkpay-data.md): BlinkPay's Blink Data product (account, balance and transaction access), condensed: permissions, metadata-driven feature detection, and the accounts, balances and transactions endpoints.

## Next

- The service and selector conventions this skill builds on: [django-services-selectors](../django-services-selectors/SKILL.md)
- Polling and background task conventions: [django-celery](../django-celery/SKILL.md)
- Exposing a payment or consent status to a frontend: [django-apis-serializers](../django-apis-serializers/SKILL.md)
