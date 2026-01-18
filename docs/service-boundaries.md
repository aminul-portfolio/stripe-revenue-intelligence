# PureLaka Enterprise — Service Boundaries

This document defines the ownership boundaries between apps, views, models, and service modules.
Goal: keep views thin, keep domain logic in services, keep data integrity rules centralized and testable.

## 1) Global architecture rules

### 1.1 Views are orchestration only
Views may:
- authenticate/authorize (RBAC)
- validate request inputs
- call services
- choose templates/serializers
- translate service errors into HTTP responses

Views may NOT:
- perform Stripe API calls directly (except via service boundary)
- implement business rules (stock, refunds, subscription state machine)
- do multi-step DB writes without a service function

### 1.2 Models are data + invariants (minimal)
Models may:
- define fields, constraints, indexes
- define minimal helpers (display, simple computed properties)

Models should NOT:
- call Stripe
- contain cross-aggregate workflows (order lifecycle, subscription state sync)

### 1.3 Services own business rules
Services:
- implement business rules and idempotency
- wrap atomic DB operations (`transaction.atomic`)
- isolate external integrations (Stripe)
- produce auditable events (audit logger)

### 1.4 Monitoring checks are read-only
Monitoring must not mutate business state except writing `DataQualityIssue` rows and snapshot rebuild operations executed explicitly.

---

## 2) Accounts / RBAC boundaries

### 2.1 accounts/*
Ownership:
- User roles: admin / ops / analyst / customer
- Role resolution for request context (context processor)
- Authorization enforcement at view boundary (who can see/run what)

Key invariants:
- Ops/Admin can run operational endpoints (orders lifecycle, monitoring tools)
- Analyst can access analytics dashboard/exports if staff+role allows
- Customers cannot access staff-only analytics/ops endpoints

Do NOT:
- hardcode permissions inside templates without server-side enforcement
- assume staff implies ops rights (role must be checked)

---

## 3) Payments app boundaries (Stripe one-off)

### 3.1 payments/services/*
Ownership:
- PaymentIntent start orchestration (server)
- Webhook routing + signature verification
- Idempotency boundary (`StripeEvent` storage / dedupe)
- Mapping Stripe events -> local domain updates (orders/refunds/stock)

Key invariants:
- Webhooks MUST be idempotent (safe to replay)
- PaymentIntent succeeded MUST mark Order paid exactly once
- Stock decrement must be locked (`select_for_update`) to prevent oversell
- Refund mapping must update Order refund fields consistently

Do NOT:
- update Order status or stock from views
- rely on client-side confirmation for business state

---

## 4) Orders app boundaries

### 4.1 orders/services/*
Ownership:
- Order creation / totals calculation
- Status transitions (cancel, fulfill) with RBAC enforcement handled in views but logic in services
- Refund state interpretation and persistence

Key invariants:
- Only Ops/Admin can run operational transitions (cancel/fulfill)
- Order is immutable after paid except via controlled workflows (refund/cancel policies)

---

## 5) Products app boundaries

### 5.1 products/services/*
Ownership:
- Stock rules (including preorder exemptions if present)
- Variant selection rules (if variants used)
- Inventory updates invoked from payment success handler

Key invariants:
- Stock can never go negative
- Inventory decrements must be atomic and locked

---

## 6) Subscriptions app boundaries (Stripe recurring)

### 6.1 subscriptions/services/stripe_subscriptions.py
Ownership:
- Create subscription (requires default payment method)
- Customer reuse strategy (session preferred; else reuse latest for user)
- Stripe reads needed to normalize status/periods/price/mrr into local row
- SQLite retry wrapper (dev safety); production recommended Postgres

Key invariants:
- “Add Card first” enforced by checking `invoice_settings.default_payment_method`
- Local subscription row created only by service; webhooks only sync existing rows
- Unix timestamp conversion uses `datetime.timezone.utc` (never `django.utils.timezone.utc`)

### 6.2 payments/services/webhook_subscription_handlers/*
Ownership:
- `subscription_updated.py`: sync local fields from Stripe `customer.subscription.updated`
- `subscription_deleted.py`: cancel local row from Stripe `customer.subscription.deleted`

Fields synced:
- status
- cancel_at_period_end
- current_period_start / current_period_end
- canceled_at / ended_at
- stripe_price_id
- mrr_pennies

Idempotency rules:
- If subscription id not found locally: ignore (no side effects)
- Multiple webhook deliveries must not cause inconsistent data

Tests:
- `payments/tests/test_subscription_webhooks.py` covers updated + deleted handler behavior

---

## 7) Analytics app boundaries

### 7.1 analytics snapshot builders
Ownership:
- Derive KPIs from raw orders/refunds
- Store daily snapshots and product rollups

Operational rule:
- Snapshots may become stale after tests or data changes; use snapshot rebuild to restore reconciliation.

---

## 8) Monitoring app boundaries

### 8.1 monitoring checks
Ownership:
- Read-only validation checks of expected invariants
- Create/resolve `DataQualityIssue` records
- `run_checks --fail-on-issues` used as CI gate

---

## 9) Audit boundaries

### 9.1 audit/services/logger.py
Ownership:
- append-only logging of key events
- called from services after state transitions and external integration actions

---

## 10) Definition-of-Done gates

After any meaningful change:
```powershell
python manage.py test
python manage.py test analyticsapp -v 2
python manage.py run_checks --fail-on-issues
