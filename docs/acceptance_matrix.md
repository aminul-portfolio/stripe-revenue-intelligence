# Acceptance Matrix — Revenue Intelligence for Stripe Commerce

This matrix maps every product claim to:
- code locations
- tests that prove it
- how to verify manually (demo steps)
- proof artifacts (where applicable)

Policy:
- If a claim is not in this matrix, it is not a shipped feature.
- If a claim has no tests, it must be labeled “manual-only” and scheduled for test coverage.

## Legend

- Status: ✅ shipped, 🟡 partial, ❌ not shipped
- Proof: tests, docs, and/or `docs/proof/*`

---

## A) Payments and Stripe correctness

### A1. Stripe PaymentIntent flow (start page produces client_secret)
- Status: ✅ shipped
- Claim: Buyer can start a payment for an order and complete checkout via Stripe PaymentIntent.
- Code:
  - `payments/views.py` (start/payment flow)
  - `payments/services/*` (intent handling as applicable)
- Tests:
  - Existing payment/access tests (project suite)
  - `orders.tests.test_payment_start_access` (access boundary)
- Manual verification:
  - With Stripe enabled (`PAYMENTS_USE_STRIPE=1`), start payment and verify PaymentIntent created.
- Proof:
  - `docs/proof/stripe_idempotency_2026-01-19.txt` (end-to-end webhook replay proves safe processing boundary)

### A2. Webhook signature verification
- Status: ✅ shipped
- Claim: Stripe webhook events are verified using Stripe signature secret.
- Code:
  - `payments/views.py` webhook endpoint
- Tests:
  - Payments webhook tests (existing suite)
- Manual verification:
  - Stripe CLI listener forwards events; endpoint returns 200 for valid signatures.
- Proof:
  - Covered by test suite (webhook signature verification tests).
  - Buyer evidence: validated during Stripe CLI smoke (see M2 Stripe proof set).

### A3. Idempotent event processing boundary (StripeEvent)
- Status: ✅ shipped
- Claim: Duplicate webhook events do not double-apply side effects.
- Code:
  - `payments/models.py` (`StripeEvent`)
  - `payments/services/*` (router/handlers)
- Tests:
  - Payments idempotency tests (existing suite; ensures StripeEvent prevents duplicates).
- Manual verification:
  - Replay the same Stripe event via Stripe CLI; confirm HTTP 200 and no duplicate effects.
- Proof:
  - `docs/proof/stripe_idempotency_2026-01-19.txt`

### A4. Refund mapping correctness (partial and full)
- Status: ✅ shipped
- Claim: Refund events update Order refund fields deterministically (status, amount, refunded_at).
- Code:
  - `payments/services/*` refund handler (maps Stripe refund events to Order fields)
  - `orders/models.py` (refund fields)
- Tests:
  - Refund mapping tests (existing suite)
- Manual verification:
  - Trigger partial and full refunds in Stripe; confirm Order updates and `run_checks` remains green.
- Proof:
  - `docs/proof/stripe_refund_partial_2026-01-19.txt`
  - `docs/proof/stripe_refund_full_2026-01-19.txt`

---

## B) Orders operations control

### B1. Order access security (owner-only / hidden 404 for non-owner)
- Status: ✅ shipped
- Claim: Users cannot view or start payments for orders they do not own.
- Code:
  - `orders/views.py` and/or access helpers
  - `payments/views.py` start endpoint access checks
- Tests:
  - `orders.tests.test_order_access`
  - `orders.tests.test_payment_start_access`

### B2. Ops endpoints protected (cancel / fulfill)
- Status: ✅ shipped
- Claim: Only Ops/Admin can cancel pending or fulfill paid orders.
- Code:
  - `orders/views.py` ops endpoints
  - `accounts/decorators.py` role enforcement
- Tests:
  - `orders.tests.test_ops_endpoints`

### B3. Stock decrement safety (oversell prevention)
- Status: 🟡 partial (implemented + tested; concurrency depth may be expanded)
- Claim: Stock is decremented safely on payment success; oversell is prevented.
- Code:
  - Payment success handler (stock decrement logic)
  - Product/variant locking as implemented
- Tests:
  - Existing orders/payments tests that cover stock decrement behavior
- Manual verification:
  - Attempt to buy beyond stock (should fail or prevent negative stock)
- Proof:
  - `docs/proof/stripe_stock_idempotency_2026-01-19.txt` (replay proves no double decrement)
- Remaining hardening (planned):
  - Concurrency stress depth (multi-worker contention) not yet proven as a dedicated test scenario.

---

## C) Monitoring and data quality controls

### C1. Monitoring runner + fail-on-issues gate
- Status: ✅ shipped
- Claim: `run_checks --fail-on-issues` is stable and can fail the build if issues exist.
- Code:
  - `monitoring/services/run_all.py`
  - `monitoring/checks/*`
  - `monitoring/models.py` (`DataQualityIssue`)
- Tests:
  - Monitoring tests (existing suite)
- Manual verification:
  - Run `python manage.py run_checks --fail-on-issues` and confirm 0 open issues when healthy.

---

## D) Analytics and revenue intelligence

### D1. Snapshot system (7/30/90 windows + daily series)
- Status: ✅ shipped
- Claim: Analytics uses snapshots for decision-grade KPIs and daily trends.
- Code:
  - `analyticsapp/models.py` (snapshot models)
  - `analyticsapp/services/snapshots.py`
  - `analyticsapp/management/commands/*` (snapshot builder)
- Tests:
  - `analyticsapp.tests.test_access` (access + smoke)
  - Any snapshot service tests present in suite
- Manual verification:
  - Run snapshot build command and view dashboard.

### D2. Executive dashboard (KPIs + charts)
- Status: ✅ shipped
- Claim: Dashboard shows KPIs for 7/30/90 and daily charts.
- Code:
  - `analyticsapp/views.py` (dashboard)
  - `analyticsapp/templates/analytics/dashboard.html`
- Tests:
  - `analyticsapp.tests.test_access`

### D3. BI-ready exports (CSV) with RBAC protection
- Status: ✅ shipped
- Claim: KPI summary, orders, products, and customers exports return CSV and are role-protected.
- Code:
  - `analyticsapp/views.py` export endpoints
- Tests:
  - `analyticsapp/tests/test_exports_csv.py`
  - `analyticsapp/tests/test_exports_csv_audit.py`
  - `accounts.tests.test_rbac_views`
- Proof:
  - `docs/proof/analytics_export_orders_audit_2026-01-19.txt`
  - `docs/proof/analytics_export_kpi_audit_2026-01-19.txt`
  - `docs/proof/analytics_export_customers_audit_2026-01-19.txt`
  - `docs/proof/analytics_export_products_audit_2026-01-20.txt`

### D4. Export actions are audited
- Status: ✅ shipped
- Claim: Export endpoints create audit events.
- Code:
  - `analyticsapp/views.py` calls `audit.services.logger.log_event`
- Tests:
  - `analyticsapp/tests/test_exports_csv.py`
  - `analyticsapp/tests/test_exports_csv_audit.py`

---

## E) Security baseline and deploy-readiness

### E1. Deploy checks pass under prod-like settings
- Status: ✅ shipped
- Claim: `python manage.py check --deploy` passes under `purelaka.settings_prod`.
- Code:
  - `purelaka/settings_prod.py`
- Tests:
  - N/A (Django system check gate)
- Manual verification:
  - `DJANGO_SETTINGS_MODULE=purelaka.settings_prod python manage.py check --deploy`
- Proof:
  - `docs/proof/m1_2026-01-19_full_gates.txt`

### E2. Gate discipline and reproducibility
- Status: ✅ shipped
- Claim: Core gates are repeatable locally and in CI.
- Proof:
  - `docs/proof/m1_2026-01-19_full_gates.txt`
  - GitHub Actions run (green)

---

## F) Documentation contracts

### F1. KPI contract is defined and maintained
- Status: ✅ shipped
- Claim: KPI definitions are the single source of truth.
- Docs:
  - `docs/kpi_definitions.md`

### F1.1 Export schema contract enforced (no silent drift)
- Status: ✅ shipped
- Claim: Export CSV headers are contract-locked; any drift fails tests.
- Contract (authoritative):
  - `docs/contracts/kpi_contract.json`
- Code:
  - Export endpoints: `analyticsapp/views.py`
- Tests:
  - `analyticsapp/tests/test_export_contract.py` (compares live CSV headers to contract file)
- Manual verification:
  - Change an export header locally and run `python manage.py test` (must fail).
- Proof:
  - `docs/proof/m3_export_contract_tests_2026-01-20.txt`

### F2. RBAC contract is defined and maintained
- Status: ✅ shipped
- Claim: RBAC rules are explicit and test-backed.
- Docs:
  - `docs/rbac_matrix.md`

---

## Out of scope (explicitly not shipped yet)

- Docker Compose buyer-ready deployment (Milestone 4)
- Runbook and demo walkthrough (Milestone 4)
- Backup/restore validation (Overlay F)
- Subscription metrics as decision-grade KPIs (only allowed once defined + snapshot-backed)
