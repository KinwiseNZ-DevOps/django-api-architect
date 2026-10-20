# Subscription lifecycle, driven by webhooks

Contents: the status model, event types and the transitions they drive, dunning, plan changes, what the customer-facing views are allowed to do

Generalised across providers (Stripe, PayPal, and similar); check the specific provider's own webhook event names and payload shape, which differ, even though the state machine below does not.

## Status model

A subscription needs more than active/inactive:

| Status | Meaning |
|---|---|
| `trialing` | In a free trial period, not yet charged |
| `active` | Paid and current |
| `past_due` | A scheduled charge failed; the provider is retrying |
| `cancelled` | Ended, by the customer or after exhausted retries; the row is kept |
| `expired` | A trial ended with no payment method attached |

Keep `current_period_end` (when the current paid or trial period ends) and `cancel_at_period_end` (the customer asked to stop, but access continues until `current_period_end`) as separate fields from status; a cancelled-but-not-yet-expired subscription is still `active` with `cancel_at_period_end=True`, not already `cancelled`.

## The webhook is the only writer of subscription state

Follow the webhook endpoint shape from django-celery (verify signature, idempotent event log, dispatcher task, per-event-type handler) and apply it here specifically:

```python
# services.py
def subscription_activate(*, provider_subscription_id, plan_id, current_period_end):
    plan = plan_for_provider_id(plan_id)  # trusted, server-side lookup; never a client-supplied plan name
    Subscription.objects.update_or_create(
        provider_subscription_id=provider_subscription_id,
        defaults={
            "plan": plan,
            "status": "active",
            "current_period_end": current_period_end,
        },
    )

def subscription_mark_past_due(*, provider_subscription_id):
    Subscription.objects.filter(provider_subscription_id=provider_subscription_id).update(status="past_due")

def subscription_cancel(*, provider_subscription_id, cancelled_at):
    Subscription.objects.filter(provider_subscription_id=provider_subscription_id).update(
        status="cancelled", cancelled_at=cancelled_at
    )
```

A customer-facing view never calls these services directly from a request the customer's own browser made; only the webhook dispatcher does, after verifying the event came from the provider.

```python
# wrong: the customer's own return redirect grants the subscription
def paypal_return(request, subscription_id, plan):
    Subscription.objects.create(user=request.user, plan=plan, status="active")  # client decided plan and status

# right: the return view only displays state the webhook already set
def paypal_return(request):
    subscription = subscription_for_user(user=request.user)
    return render(request, "subscription_pending.html" if subscription.status == "trialing" else "subscription_active.html")
```

## Event types and the transition each drives

| Event (typical name, varies by provider) | Transition |
|---|---|
| Subscription created / first payment succeeded | `trialing` or (no trial) straight to `active`; set `current_period_end` from the event |
| Renewal payment succeeded | stays `active`; advance `current_period_end` |
| Payment failed | `active` -> `past_due` (see Dunning) |
| Subscription cancelled (by customer or after retries exhausted) | -> `cancelled`, set `cancelled_at`; keep the row |
| Trial ended with no payment method | `trialing` -> `expired` |
| Plan changed | update `plan`; most providers prorate the current period automatically, so don't also compute proration locally unless the provider's event says it did not |

Treat an event type the handler doesn't recognise as a no-op, logged for visibility, not an error; providers add event types over time.

## Dunning: a failed payment is not a cancellation

Providers retry a failed renewal over a schedule (commonly days, not hours) before giving up. Move the subscription to `past_due` on the first failure and show the customer a "payment failed, please update your card" state; do not cancel, delete, or lock out their access immediately. Only transition to `cancelled` when the provider's own "retries exhausted" event arrives, or the customer cancels directly. A `past_due` subscription that later receives a successful renewal event goes straight back to `active`.

## Plan changes (upgrade and downgrade)

A plan change is a provider-side operation (most providers have a dedicated "update subscription" or "change plan" call) followed by the same webhook-driven update as any other state change; it is not two independent local writes. Do not decide the new price locally and write it on the customer's return redirect; wait for the provider's confirmation event, exactly as with activation. If a change needs the customer's fresh approval (a plan swap that is not a simple provider-side revision), redirect them to the provider's own approval flow and update local state only once its webhook confirms it, the same return-is-not-proof principle as django-open-banking.

## Mobile app store subscriptions (Apple, Google)

A Flutter app selling a subscription through Apple's or Google's in-app purchase system follows the same webhook-is-the-source-of-truth principle as PayPal or Stripe, with two differences: both platforms are explicit that their notification alone is not enough, and each has its own extra states beyond the generic ones above.

**Apple (App Store Server Notifications V2).** Apple posts a signed JWS to a URL set in App Store Connect on every transaction or subscription change (`SUBSCRIBED`, `DID_RENEW`, `DID_FAIL_TO_RENEW`, `EXPIRED`, `REFUND`, `GRACE_PERIOD_EXPIRED`, and others). Verify the JWS signature and its certificate chain to Apple's root CA before trusting anything in it; Apple publishes an App Store Server Library that does this. Deduplicate on `notificationUUID`, since the same notification can arrive more than once. A `DID_FAIL_TO_RENEW` with subtype `GRACE_PERIOD` means keep serving the subscription for now; the App Store keeps retrying billing for up to 60 days before `GRACE_PERIOD_EXPIRED` arrives and access should actually stop.

**Google Play (Real-time developer notifications).** Google publishes a base64-encoded message to a Cloud Pub/Sub topic, containing only a `notificationType` (`SUBSCRIPTION_RENEWED`, `SUBSCRIPTION_CANCELED`, `SUBSCRIPTION_ON_HOLD`, `SUBSCRIPTION_IN_GRACE_PERIOD`, `SUBSCRIPTION_PAUSED`, and others) and a `purchaseToken`. Google's own documentation is explicit that this is a signal only: "these notifications tell you only that the purchase state changed; they do not give you complete information about the purchase." Always call the Google Play Developer API with the `purchaseToken` to read the actual current state before changing anything locally. Android adds states the others don't have in quite the same shape: `account hold` (billing failed, access suspended but not yet cancelled) and `paused` (the customer deliberately paused a subscription for a fixed period, not a failure at all); map both onto this skill's status model rather than treating either as a plain cancellation.

**Shared rules for both.** Store the platform's own identifier (`originalTransactionId` for Apple, `purchaseToken` for Google) the same way `provider_subscription_id` is used above. Never grant access from the client reporting "the purchase succeeded"; the Flutter `in_app_purchase` plugin (or any store SDK) reports a purchase to the app first, and that report must be verified against the platform's server API before the backend treats it as real, exactly like a payment redirect is never trusted on its own. A purchase the backend hasn't verified yet should show as pending, the same as a trialing or awaiting-confirmation subscription elsewhere in this file.

## Cancellation never deletes

```python
# wrong
def delete_subscription(request, subscription_id):
    cancel_with_provider(subscription_id)  # response not checked
    Subscription.objects.get(provider_subscription_id=subscription_id).delete()

# right: check the provider call succeeded, then soft-cancel through the
# same webhook-driven service every other state change goes through
def subscription_cancel_requested(*, subscription):
    response = cancel_with_provider(subscription.provider_subscription_id)
    if not response.ok:
        raise SubscriptionCancelError(response.text)
    # the provider's own cancellation webhook event will call subscription_cancel()
    # above; this view does not set status itself
```
