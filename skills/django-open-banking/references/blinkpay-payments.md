# BlinkPay: Blink Payments

Contents: authentication, choosing a consent type, choosing a flow, consent and payment states, timing rules, payment limits, never trusting the redirect, idempotency, other error codes, refunds, mobile clients, redirect URI whitelisting

BlinkPay is a New Zealand open banking payment gateway (PayNow for single payments, AutoPay for recurring). Condensed from BlinkPay's own developer documentation; check it directly for anything this file does not cover, since it is the source of truth.

## Authentication

OAuth 2.0 client credentials, one token per product (Blink Payments and Blink Data have separate token endpoints and separate client IDs). `POST /oauth2/token` with `grant_type=client_credentials`, `client_id`, `client_secret`. The token expires in 3600 seconds; cache it server-side and refresh a few minutes before expiry, not per request. Client ID and secret live only in the adapter's config, sourced from environment variables or a secret manager, never in a migration, a fixture, or anywhere a client can read them.

A 401 on a token request or an API call carries an empty body; branch on the HTTP status, not on parsed error text. A 429 carries `Retry-After`; back off at least that long, then exponentially with jitter on repeat.

## Choosing a consent type

| Need | Use |
|---|---|
| Customer must review the exact amount before approval, or payment timing needs to be deferred up to 48 hours | Single consent, then `POST /payments/v1/payments` with only the `consent_id` |
| Simplest one-off checkout, amount fixed at consent time, pay immediately on return | Quick payment: one `POST`, then one `GET` to complete it |
| Subscription or recurring billing with variable amounts inside a limit | Enduring consent: set `maximum_amount_payment`, `maximum_amount_period`, `period`, `from_timestamp`, optional `expiry_timestamp` |

For most checkouts, a quick payment is the right default; reach for a single consent only when the project genuinely needs to defer the payment call.

## Choosing a flow

Use the Gateway flow (`"flow": {"detail": {"type": "gateway", "redirect_uri": ...}}`) unless there is a specific reason not to. It hosts bank selection and both the redirect and decoupled authentication paths itself, adapts automatically as banks change, and needs no bank-specific code in the project. Only drop to the Redirect or Decoupled flow directly when the project needs full control of the bank-selection UI.

## Consent and payment are separate state machines

A consent's state tracks whether the customer approved something. A payment's state tracks whether money actually moved. Do not conflate them.

**Consent states:** `GatewayAwaitingSubmission` (gateway only) → `AwaitingAuthorisation` → `Authorised` → `Consumed`, or `Rejected` / `Revoked` / `GatewayTimeout` along the way. `Consumed` means the consented action is finished, not that a payment succeeded: a single consent whose payment the bank rejected after accepting it is also `Consumed`.

**Payment states:** `Pending` → `AcceptedSettlementInProcess` → `AcceptedSettlementCompleted`, or `Rejected`. `AcceptedSettlementCompleted` is the only status that means the payer's bank sent the funds; treat every other state, including `AcceptedSettlementInProcess`, as not yet settled. This is the one field `get_payment_status` in the provider interface should map to its `settled` flag.

Read `consent.payments[0]` for the latest payment record; a consent that never reached the bank (revoked, or timed out before authorisation) has an empty `payments` array, so check `consent.status` for that case specifically.

## Payment limits

Each bank sets its own minimum and maximum per payment, and they differ between a single/quick payment and an AutoPay payment. The minimum is $0.01. Read the current per-bank maximum from `payment_limit` on `GET /payments/v1/meta` rather than hard-coding one; a payment over it is rejected with 400 BP229. Check this before creating a consent for an amount that might exceed a bank's limit, not only after the rejection.

## Timing rules

- A single consent must be paid within 48 hours of becoming `Authorised`, or it becomes `Rejected`.
- A card quick payment still pending 24 hours after authorisation is cancelled and marked `Rejected` automatically.
- A Gateway consent times out after 15 minutes if the customer never starts authorisation; once at the bank, that bank's own window applies (roughly 4 to 10 minutes).
- Poll a payment every second for at most a minute or two once the customer returns; don't poll while they are still at their bank. On the direct decoupled flow with no callback, poll every 5 seconds instead.

## Never trust the redirect

A return to your `redirect_uri` carries `cid` and, only on a non-success outcome, `status` and a customer-safe `error` string that can change without notice. A return with `cid` and no `status` is not confirmation of success; it means the outcome was not reported as a failure. Always call `GET` on the consent or quick payment server-side before acting on it, and branch on the typed status field from that call, never on the `error` text or the mere presence of `cid`. The decoupled flow's `callback_url` is unsigned and carries only the consent ID; treat it exactly the same way, as a prompt to poll, not as the outcome.

## Idempotency

Send an `idempotency-key` header (a UUID) on every request that creates a consent, payment or refund. Generate one key per distinct business action and send the same key again on a retry of that same action after a timeout or 5xx; a new key on retry risks a duplicate payment. Gateway-flow consents are de-duplicated on a `request-id` header instead; send a UUID there and reuse it on retry. Relevant error codes:

| Code | HTTP | Meaning |
|---|---|---|
| BP702 | 409 | Same idempotency key, different payload: a bug, not a retry |
| BP703 | 409 | The payment this key created is still in flight; poll it, don't resubmit |
| BP708 | 409 | A request with this key is still being processed; retry shortly with the same key |
| BP710 | 409 | The key was already used by a now-terminal payment; read its status before deciding whether a fresh key is needed |

Never create a new consent for the same order until the old one is confirmed to have no payment that may still settle: `GET` the consent and check `payments[0]` first. Creating a second consent while the first might still settle risks charging the customer twice. After a genuine rejection, a fresh idempotency key is correct; reusing the old key on a new attempt just returns the rejected payment again.

## Other error codes worth knowing by name

| Code | HTTP | Meaning |
|---|---|---|
| BP002 | 422 | Consent already consumed or rejected (including a single consent not paid within 48 hours) |
| BP015 | 422 | Consent revoked, often by the customer in their banking app; create a new one |
| BP018 | 422 | `POST /payments` called on a quick payment; `GET` it instead |
| BP214 | 400 | `redirect_uri` is not on the whitelisted list for this environment |
| BP235 | 400 | `amount` or `pcr` sent when paying against a single consent; send only `consent_id` |

## Refunds

One endpoint, `POST /payments/v1/refunds`, always with an `idempotency-key`. What it does depends on how the customer paid: a bank payment refund (`type: account_number`) does not move money, it returns the payer's account number so the project pays them back itself; a card payment refund (`full_refund` or `partial_refund`) actually returns funds through the card network. A refund is only possible once the payment is `AcceptedSettlementCompleted` (BP012 otherwise), and the total refunded can never exceed the amount charged (BP039). Card refunds have a 60-day window (BP045); account-number refunds do not.

## If the client is a mobile app

The backend rules above are unchanged, but the redirect target is not a web page. BlinkPay requires the bank step to open in the system browser or an in-app browser tab (`SFSafariViewController` or `ASWebAuthenticationSession` on iOS, Chrome Custom Tabs on Android), never an embedded WebView. A custom URL scheme such as `myapp://callback` is accepted as a `redirect_uri` provided it has a host part (`myapp://callback`, not `myapp:callback`), and still needs whitelisting like any other redirect URI. The mobile client should re-check payment status when the app returns to the foreground, not rely solely on the scheme callback firing. See the `flutter-django-integration` skill in the flutter-developer repo for the client side of this.

## Redirect URI whitelisting

`redirect_uri` must exactly match an entry registered in the BlinkPay portal for the environment in use (sandbox and production keep separate lists). Register the specific return path, not a bare domain: path matching is a prefix match on the raw string, so register a path ending in a distinct segment (`/blinkpay/return`, not `/`). A trailing slash in the registered entry rejects the slash-less form. This is operational setup in the BlinkPay portal, not something the Django project can work around in code.
