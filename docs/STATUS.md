# STATUS — Revenue Intelligence for Stripe Commerce

## Current milestone

* Milestone: **M3 Hardening (in progress)**
* Current step: **M3.3 Buyer proof-pack index complete (see Contracts & Proof Index)**
* M2 closed: **2026-01-20** (exit proofs complete; gates verified)

## Runtime baseline

* Python: 3.12.3
* Framework: Django 5.2.10
* DB (dev): SQLite
* Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)

## Release gates (latest verified: 2026-01-21)

All gates below must remain green locally and in CI.

* `python manage.py check`: PASS
* `python manage.py test`: PASS (**59 tests**)
* `python manage.py run_checks --fail-on-issues`: PASS (**open=0, resolved=3**)
* `python manage.py makemigrations --check --dry-run`: PASS
* `ruff check .`: PASS
* `ruff format --check .`: PASS
* `pip-audit -r requirements.txt`: PASS (no known vulnerabilities)
* Deploy gate (prod-like settings): `python manage.py check --deploy`: PASS

  * Run with: `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`

### Important settings note (prevents false test failures)

* `purelaka.settings_prod` enables deployment protections such as `SECURE_SSL_REDIRECT=True`.
* If you run the test suite with `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`, Django’s test client can receive **301 redirects to `https://testserver/`** for many endpoints.
* Therefore:

  * Run **tests and normal gates** with default settings (`purelaka.settings`).
  * Run **deploy gate only** with prod settings:

    * `DJANGO_SETTINGS_MODULE=purelaka.settings_prod python manage.py check --deploy`
  * After running the deploy gate in PowerShell, clear it:

    * `Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue`

> Note: PowerShell may show a `NativeCommandError` banner when piping/redirection is used (e.g., `Tee-Object`) even if the command succeeds. Treat `$LASTEXITCODE=0` as the authoritative success signal and keep outputs as proof.

## Notes (chronological)

* 2026-01-21: Payments hardening proof captured: stock idempotency tests (docs/proof/m3_payment_intent_stock_idempotency_tests_2026-01-21.txt).

* 2026-01-18: Monitoring namespace + smoke test stabilized; templates fixed to use namespaced URL reverse.
* 2026-01-19: CI confirmed green on `main` for core gates and engineering gates.
* 2026-01-19: Runbook updated with fresh install steps and local/CI gate parity (`docs/runbook.md`).
* 2026-01-19: RBAC regression resolved; roles service updated with deterministic role assignment for tests/support.
* 2026-01-19: Analytics exports hardened:
  * CSV exports protected by RBAC (ops/analyst/admin allowed; customer denied/hidden).
  * Export actions generate audit events (verified by tests).
  * Added export tests for CSV + audit expectations.
* 2026-01-19: Deploy gate made reproducible:
  * Introduced `purelaka/settings_prod.py` for `check --deploy` (prod-like toggles).
  * HSTS flags set to satisfy deploy checks in prod-like mode.
  * Confirmed that leaving `DJANGO_SETTINGS_MODULE` set to `settings_prod` can cause test redirects (301); added policy to prevent confusion.
* 2026-01-19: Migration drift fixed:
  * Added `orders/migrations/0005_alter_order_status.py`.
  * `makemigrations --check --dry-run` now clean.
* 2026-01-19: Environment discipline reinforced:
  * `.env` is local-only and must never be committed.
  * Local Stripe replay artifacts (`tmp_*.json`) are ignored via `.gitignore`.
* 2026-01-19: Stripe live smoke validated locally (Stripe CLI → `/payments/webhook/`) with HTTP 200 processing.
* 2026-01-19: Stripe webhook replay proven idempotent:
  * Same Stripe event replay returns HTTP 200.
  * No duplicate `StripeEvent` rows created for the same `event_id`.
* 2026-01-19: Stripe webhook replay proven stock-safe:
  * Replaying the same event does not double-decrement stock.
* 2026-01-19: Stripe refunds proven end-to-end:
  * Partial refund updates `Order` refund fields (`refund_status=partial`, pennies updated, `refunded_at` set) and `run_checks` remains green.
  * Full refund updates `Order` refund fields (`refund_status=full`, pennies updated, `refunded_at` set) and `run_checks` remains green.
* 2026-01-19: Analytics export proofs captured from a logged-in superuser session:
  * Orders CSV export returns attachment and writes `AuditLog(event_type=analytics_export)`.
  * KPI summary CSV export returns attachment and writes `AuditLog(event_type=analytics_export)`.
* 2026-01-20: Remaining analytics exports proven and audited:
  * Customers CSV export returns attachment and writes `AuditLog(event_type=analytics_export)`.
  * Products CSV export returns attachment and writes `AuditLog(event_type=analytics_export)`.
* 2026-01-20: KPI export schema contract baselined as machine-checkable JSON (`docs/contracts/kpi_contract.json`) to prevent header drift.
* 2026-01-20: Export schema contract tests added; CSV headers enforced against `docs/contracts/kpi_contract.json`.
* 2026-01-20: Acceptance matrix expanded to trace buyer-facing claims → code → tests → proofs (`docs/acceptance_matrix.md` + proof snapshot).
* 2026-01-20: RBAC surface contract test added and stabilized using namespaced URL reversing for monitoring (`reverse("monitoring:monitoring-issues")`) + proof captured.
* 2026-01-20: Contracts & Proof Index added as the buyer due-diligence entry point (`docs/CONTRACTS_AND_PROOFS.md`).
* 2026-01-20: KPI definitions updated (time window boundaries clarified; export contract references reinforced) (`docs/kpi_definitions.md`).
* 2026-01-21: Deploy gate proof upgraded to be self-auditing (timestamp + `DJANGO_SETTINGS_MODULE` + env-cleared confirmation).
* 2026-01-21: Consolidated M3 gates proof captured as a buyer-ready snapshot (`docs/proof/m3_2026-01-21_full_gates_clean.txt`).
* 2026-01-21: Payments hardening proof captured: oversell prevention tests (`docs/proof/m3_stock_oversell_prevention_tests_2026-01-21.txt`).

## Evidence (proof artifacts)

### M1 consolidated proof (authoritative)

* `docs/proof/m1_2026-01-19_full_gates.txt`

> Policy: prefer a single consolidated proof per milestone over many fragmented proof files.

### M2 exit proofs (authoritative set)

Stripe safety + refunds:

* `docs/proof/stripe_idempotency_2026-01-19.txt`
* `docs/proof/stripe_stock_idempotency_2026-01-19.txt`
* `docs/proof/stripe_refund_partial_2026-01-19.txt`
* `docs/proof/stripe_refund_full_2026-01-19.txt`

Exports audited (attachments + audit events):

* `docs/proof/analytics_export_orders_audit_2026-01-19.txt`
* `docs/proof/analytics_export_kpi_audit_2026-01-19.txt`
* `docs/proof/analytics_export_customers_audit_2026-01-19.txt`
* `docs/proof/analytics_export_products_audit_2026-01-20.txt`

### M3 proof pack (current)

Buyer entry point: `docs/CONTRACTS_AND_PROOFS.md`

Contracts + tests:

* `docs/kpi_definitions.md`
* `docs/contracts/kpi_contract.json`
* `analyticsapp/tests/test_export_contract.py`
* `docs/proof/m3_export_contract_tests_2026-01-20.txt`
* `docs/proof/m3_export_contract_test_verbose_2026-01-20.txt`
* `docs/proof/m3_kpi_contract_alignment_2026-01-20.txt`
* `docs/proof/m3_kpi_inventory_2026-01-20.txt`
* `docs/proof/m3_kpi_contract_completeness_2026-01-21.txt`


Payments hardening:

* `payments/tests/test_payment_intent_stock_idempotency.py`
* `docs/proof/m3_payment_intent_stock_idempotency_tests_2026-01-21.txt`

Claim traceability:

* `docs/acceptance_matrix.md`
* `docs/proof/m3_acceptance_matrix_2026-01-20.txt`

RBAC surface contract:

* `docs/rbac_matrix.md`
* `accounts/tests/test_rbac_surface_contract.py`
* `docs/proof/m3_rbac_surface_contract_2026-01-20.txt`

Consolidated M3 gates proof (authoritative):

* `docs/proof/m3_2026-01-21_full_gates_clean.txt`
* `scripts/gates.ps1`
* `scripts/deploy_gate.ps1`
* `docs/proof/m3_deploy_gate_2026-01-21.txt`
* `docs/proof/m3_kpi_contract_completeness_2026-01-21.txt`
  * Includes timestamp + DJANGO_SETTINGS_MODULE + env cleared confirmation.

## Completed

### Milestone 1 — Audit-clean & runnable (complete)

* Wishlist included and wired (routes/templates/tests).
* Monitoring checks stable; negative-case proven (open → resolved workflow).
* Deterministic tests: pass with `PAYMENTS_USE_STRIPE=0`.
* Repo hygiene: `.env`, db, venv excluded; proofs stored under `docs/proof/`.
* CI established and green on `main` (quality + security gates).
* Deploy gate reproducible via `purelaka.settings_prod` and `check --deploy`.
* Full gate proof captured in `docs/proof/m1_2026-01-19_full_gates.txt`.

### Milestone 2 — Operations Control hardened (complete)

* Order lifecycle rules enforced and tested (cancel/fulfill paths; access boundaries).
* Refund mapping updates order refund fields; reconciliation checks stable.
* Stock decrement/oversell prevention present; idempotent on webhook replay (proven).
* RBAC boundaries enforced across analytics/exports/monitoring/orders/payments.
* Audit logging present for operational actions; analytics exports audited (proven).

## In progress

### Milestone 3 — Hardening (in progress)

* KPI meaning contract strengthened (`docs/kpi_definitions.md`) and aligned to the windows policy (inclusive of today).
* Export schema contract baselined as machine-checkable JSON (`docs/contracts/kpi_contract.json`) and enforced via tests (`analyticsapp/tests/test_export_contract.py`).
* Acceptance matrix maintained as the buyer-facing claim map (`docs/acceptance_matrix.md`) with a dated snapshot in `docs/proof/`.
* RBAC matrix remains the source of truth and is test-backed; RBAC surface contract test added to prevent accidental exposure (`accounts/tests/test_rbac_surface_contract.py`).
* Buyer due-diligence entry point is now centralized in `docs/CONTRACTS_AND_PROOFS.md`.
* Consolidated M3 gates proof captured: `docs/proof/m3_2026-01-21_full_gates_clean.txt`.
* Deploy gate proof captured: `docs/proof/m3_deploy_gate_2026-01-21.txt`.

## Top blockers (max 3)

1. **KPI contract completeness:** ensure every KPI shown/exported is defined and matches implementation (units, sources, edge cases, and window logic).
2. **Hardening coverage gaps:** expand tests for concurrency depth (stock/oversell) and any remaining "manual-only" claims in the acceptance matrix.
3. **Buyer-grade packaging:** Postgres + Docker Compose deployment path is not yet implemented (Milestone 4).

## Next 3 actions (strict, step-by-step)

1. **KPI contract completeness sweep (M3):** enumerate all KPI fields used by snapshots/dashboard/exports and confirm each is defined in `docs/kpi_definitions.md` with units + edge-case handling.
2. **Concurrency hardening tests (M3):** add at least one deterministic test that exercises stock decrement/oversell prevention under contention (or the closest reliable approximation in the Django test runner).
3. **Begin M4 deployment baseline:** introduce Docker Compose + Postgres and prove parity gates (migrate + test + run_checks) on Postgres locally.
