---
name: django-subscriptions
description: >
  Use when building or changing a subscription plan, activation flow,
  cancellation, upgrade or downgrade, or a billing webhook or app store server
  notification. Governs subscription lifecycle management in Django API
  projects. Do not use for the open banking payment-consent mechanics themselves
  (django-open-banking), for a one-off payment with no recurring plan, or for
  Celery task mechanics in general (django-celery).
---

# Django Subscriptions

Stance: a subscription's state is decided by the billing provider and learned through its webhook, never by the customer's own browser request; the specific provider and plan model are flexible. Soft-cancel, never delete.

## Hard rules

- A subscription's status, plan and billing dates are set only by a verified webhook handler (or an equivalent signed server-to-server callback), never by a view the customer's browser reaches directly. Mechanism: a return URL or redirect is fully client-controlled and replayable; treating it as the source of truth lets a customer grant themselves access by guessing or replaying it.
- Never delete a subscription row on cancellation. Mechanism: deleting destroys the audit trail needed to reconcile "did billing actually stop", and if the provider-side cancel call fails partway, deleting the local row anyway leaves your system and the provider disagreeing with no record that it happened. Fix: set a status and `cancelled_at`, keep the row.
- Check the provider's response before trusting a cancel or update succeeded. Mechanism: issuing the provider call and then unconditionally changing local state regardless of the response repeats the same trust failure a forged redirect would cause, just from the other direction.
- A plan's price comes from a server-side mapping, never a client-supplied plan name or price. Mechanism: if a view decides the price from a request parameter, a modified request can claim any plan at any price.
- A failed payment moves a subscription to a distinct `past_due` state, never straight to cancelled. Mechanism: providers retry failed payments over days before giving up; cancelling on the first failure loses recoverable revenue and surprises a customer whose card was simply retried successfully a day later.
- Catch the specific exception a missing subscription raises, never a bare `except:`. Mechanism: a bare except also swallows an unrelated bug (a typo, a missing import) and reports it as "no subscription", hiding the real failure.
- Act only on what the user asked. Before answering or changing anything, open the relevant files and check what is already done; report only what you checked, never guess, and do not redo finished work. Reason: guesses and repeated work waste the user's credit.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| Creating, activating, cancelling, or changing a subscription's plan | Continue; state changes come from a verified webhook, not a customer-facing view |
| A payment on a subscription fails | Continue; see dunning in [webhook-lifecycle.md](references/webhook-lifecycle.md), do not cancel on the first failure |
| No webhook endpoint exists yet, and subscription state is set directly from a return-redirect view | Flag this as the gap to close before building anything else on top |
| A one-off, non-recurring payment | This skill does not apply; see django-open-banking (bank payment) or treat it as a normal third-party integration |

## Steps

1. **Detect.** Find the subscription app, its models, and whichever of these exist: a provider adapter, a webhook endpoint, a plan registry. Note which are missing.
2. **Fix or build.**
   - Model a subscription with a real status (`trialing`, `active`, `past_due`, `cancelled`, `expired`), `current_period_end`, and `cancel_at_period_end`, not a bare `is_active` boolean. Keep the row on cancellation; add `cancelled_at`, don't delete.
   - Map a plan to its price from a trusted, server-side source (a `Plan` model or a static registry keyed on the provider's own plan id), never from a plan name a client supplies in a request.
   - Build the webhook endpoint the same way django-celery already specifies for any webhook provider: verify the signature, log the event idempotently, dispatch to a handler per event type, acknowledge quickly, skip an event already processed. See [webhook-lifecycle.md](references/webhook-lifecycle.md) for the subscription-specific event types and the status transitions each one drives.
   - A customer-facing return view (after checkout, after updating a plan) only shows a waiting or confirmation page; it reads the subscription's current state to display it, and never sets that state itself.
   - On a failed payment, follow the provider's own retry schedule (dunning) and move the subscription to `past_due`, not `cancelled`; only cancel when the provider reports the retries exhausted or the customer cancels.
   - Catch the specific exception (`Subscription.DoesNotExist`), never a bare `except:`.
3. **Verify.** Tests cover: an unsigned or forged webhook is rejected, a client-supplied plan name cannot set the price, cancelling preserves the row and its history, a payment-failure event moves status to `past_due` without deleting anything, and a duplicate webhook delivery is a no-op.

## References

- [webhook-lifecycle.md](references/webhook-lifecycle.md): the status enum, the webhook event types and the state transition each drives, dunning, plan changes, and Apple/Google app store notifications, generalised across providers.

## Next

- The webhook endpoint shape itself (signature verification, idempotent event log, dispatcher): [django-celery](../django-celery/SKILL.md)
- Where the subscription-changing logic itself lives: [django-services-selectors](../django-services-selectors/SKILL.md)
- A one-off bank payment instead of a subscription: [django-open-banking](../django-open-banking/SKILL.md)
