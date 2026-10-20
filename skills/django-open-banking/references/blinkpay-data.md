# BlinkPay: Blink Data

Blink Data is BlinkPay's account information product: read-only access to a customer's accounts, balances, transactions and statements, once they consent. Condensed from BlinkPay's own developer documentation; check it directly for anything this file does not cover.

## Authentication

Its own OAuth 2.0 client credentials flow, separate from Blink Payments: a separate token endpoint, client ID and secret, even though both products are managed from the same BlinkPay portal. Cache and refresh the same way as the payments token (see blinkpay-payments.md); the two tokens are not interchangeable.

## Permissions drive both the consent and the endpoints

Request only the permissions a feature actually needs; the customer sees exactly what they are being asked to share.

| Permission | Lets you call |
|---|---|
| `ReadAccounts` | `GET /v1/accounts`, `GET /v1/accounts/{account_id}` |
| `ReadBalances` | `GET /v1/accounts/{account_id}/balances` |
| `ReadTransactions` | `GET /v1/accounts/{account_id}/transactions` |
| `ReadStatements` | `GET /v1/accounts/{account_id}/statements` and its sub-paths |
| `ReadParty` | `GET /v1/party`, `GET /v1/accounts/{account_id}/party` |

Calling an endpoint the consent's permissions don't cover returns 403. Not every bank supports every permission, statements especially (most support at least 2 years of history, but availability varies); check `GET /v1/meta` before requesting a permission or building a feature around it, rather than discovering the gap from a customer's rejected consent.

## Consent date rules

- `start_date_time` cannot be in the future.
- `end_date_time`, if set, must be after today's New Zealand date; omit it to read up to the latest transaction.
- `start_date_time` and `end_date_time` must be on different dates.
- `expiration_date_time` is optional (omit for a consent with no expiry), cannot fall on the creation day, and cannot fall before `start_date_time` or `end_date_time`.
- Some banks cap how far back `start_date_time` can go regardless of what BlinkPay allows (for example, one major bank accepts no more than 2 years back); treat any bank-specific limit from `GET /v1/meta` as authoritative over a project's own default range.
- Every date-time is ISO 8601 with an explicit offset (`2026-03-20T15:30:00+13:00`), never a bare date.

## Never trust the redirect here either

The same rule from Blink Payments applies: a return to your `redirect_uri` is a prompt to check, not proof of anything. Confirm the consent's status server-side with `GET` before granting the application access that depends on it, and branch on the typed status, not on which query parameters happen to be present.

## Reading data correctly

- **Metadata first.** `GET /v1/meta` returns one entry per bank enabled for the organisation, each with a `features` object (`accounts`, `balances`, `transactions`, `statements`, `party`). `bank_id` differs between sandbox and production; match on the bank's `name`, never a hard-coded ID. Cache the response for about a day.
- **Amounts are unsigned; `direction` carries the sign.** Every `amount.amount` string in balances and transactions is unsigned. A transaction's `direction` (`in` or `out`) tells you whether it added or removed money; apply the sign yourself rather than parsing one out of the string.
- **`transaction_id` is optional.** Some banks don't send one. Don't use it alone as a unique key for deduplication; combine it with the account, amount and `date_time`, or accept that exact duplicate detection is bank-dependent.
- **`type` is the bank's own code, passed through unchanged.** Its values differ by bank, so don't branch application logic on it across banks; use `direction` and the optional `merchant`/`reference` fields instead.
- **Reference parties are fixed by role.** In a transaction's `reference`, `from_party` is always the payer and `to_party` is always the payee, regardless of `direction`; don't assume `from_party` means "the other side of a credit" versus "the other side of a debit".
- **Pagination.** `page` and `size` (`size` capped at 500) on every list endpoint; always read `total_pages` rather than assuming one page is everything.

## Error codes (BDT-prefixed)

| Code | HTTP | Meaning |
|---|---|---|
| BDT211 | 400 | `redirect_uri` is not on the whitelisted list for this environment |
| BDT213 | 400 | The requested bank is not enabled for this organisation |
| BDT260 | 400 | A gateway consent's `flow_hint` is missing `bank` |
| BDT412 | 403 | The consent has expired |
| BDT701 | 409 | Same `idempotency-key`, different request body |

Blink Data's whitelisting and idempotency codes mirror Blink Payments' BP-prefixed ones in meaning but use their own BDT-prefixed codes; don't assume a BP code applies to a Blink Data call or vice versa.
