# Provider-agnostic interface

Contents: app shape, the payment interface, the data interface, provider registry and selection, what an adapter owns, where polling belongs

Open banking covers two separable products: initiating a payment, and reading account data. A project may need one, or both, and they get separate interfaces so a provider that only does one is not forced to stub the other.

## App shape

An `open_banking` app pack (or a name that fits the project) holds this alongside the usual `models.py`, `services.py`, `selectors.py`, `apis.py`, `tasks.py`:

```
open_banking/
  models.py          PaymentConsent, Payment, DataConsent (your own records)
  providers/
    base.py           the two interfaces below
    blinkpay.py        the BlinkPay adapter
    registry.py        maps a provider name/country to its adapter instance
  services.py          calls the active adapter, never a provider SDK directly
  selectors.py
  tasks.py             polling tasks
```

`providers/` is the only place that imports a provider's SDK or constructs its requests. Everything else, including `services.py`, talks to the interface in `base.py`.

## Payment interface

```python
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class PaymentConsentResult:
    provider_consent_id: str
    redirect_url: str | None  # None for a decoupled-only flow
    status: str  # the adapter's own small enum, mapped from the provider's


@dataclass(frozen=True)
class PaymentStatusResult:
    status: str
    settled: bool  # the one field callers trust for "money moved"
    provider_payment_id: str | None


class PaymentProvider(Protocol):
    def create_single_payment(
        self,
        *,
        amount: Decimal,
        currency: str,
        reference: str,
        idempotency_key: str,
        return_url: str,
    ) -> PaymentConsentResult: ...

    def create_recurring_consent(
        self,
        *,
        max_amount_per_payment: Decimal,
        max_amount_per_period: Decimal,
        period: str,
        currency: str,
        idempotency_key: str,
        return_url: str,
    ) -> PaymentConsentResult: ...

    def take_recurring_payment(
        self,
        *,
        provider_consent_id: str,
        amount: Decimal,
        currency: str,
        reference: str,
        idempotency_key: str,
    ) -> PaymentStatusResult: ...

    def get_payment_status(self, *, provider_consent_id: str) -> PaymentStatusResult: ...

    def refund_payment(
        self,
        *,
        provider_payment_id: str,
        idempotency_key: str,
        amount: Decimal | None = None,
    ) -> str: ...  # returns a provider refund id; poll its status separately
```

`amount`, `currency` and `reference` are parameters the service passes in from its own order or subscription record; nothing in `providers/` ever reads them from a request body. `status` on the result types is the adapter's own small set of values (for example `awaiting_authorisation`, `authorised`, `settled`, `rejected`), not the provider's own strings, so a second provider can map onto the same set.

## Data interface

```python
@dataclass(frozen=True)
class DataConsentResult:
    provider_consent_id: str
    redirect_url: str | None
    status: str


class DataProvider(Protocol):
    def create_data_consent(
        self,
        *,
        permissions: list[str],  # your own permission names; the adapter maps them
        expires_at: "datetime",
        return_url: str,
    ) -> DataConsentResult: ...

    def get_consent_status(self, *, provider_consent_id: str) -> str: ...

    def list_accounts(self, *, provider_consent_id: str) -> list[dict]: ...

    def get_balances(self, *, provider_consent_id: str, account_id: str) -> list[dict]: ...

    def get_transactions(
        self,
        *,
        provider_consent_id: str,
        account_id: str,
        from_date: "datetime",
        to_date: "datetime | None" = None,
    ) -> list[dict]: ...
```

Keep the account, balance and transaction return shapes as adapter-normalised dicts (or typed dataclasses, once a second provider shows which fields are genuinely common) rather than passing a provider's raw response up; a second provider's field names and nesting will differ.

## Registry and selection

```python
# providers/registry.py
def get_payment_provider(*, country: str = "NZ") -> PaymentProvider:
    if country == "NZ":
        return BlinkPayAdapter()
    raise ValueError(f"No payment provider configured for {country}")
```

A project with one provider can skip the country parameter and return a singleton; keep the function signature ready to take one once a second provider exists, rather than threading a provider choice through every caller later.

## What the adapter owns, and what it must not do

The adapter owns: authenticating with the provider, caching and refreshing its own access token, building the provider's request shape, mapping the provider's status values onto the interface's small enum, and deciding which one field means "settled" or "consent is current" for that provider.

The adapter must not: accept an amount, currency, permission list or reference from anywhere other than its own method parameters; store the provider's access token anywhere callers can read it; or leak provider-specific status strings past its own return types.

## Where polling belongs

A Celery task (see django-celery) calls `get_payment_status` or `get_consent_status` through the service layer, on a bounded schedule, and upserts the local record with `update_or_create` keyed on the provider's own ID. A redirect return or an unsigned callback ping triggers one extra poll outside the schedule; it never carries the status itself.
