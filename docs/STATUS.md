# STATUS — Revenue Intelligence for Stripe Commerce

## Current milestone

* Milestone: **M2 Operations Control hardened (in progress)**
* Current step: **M2 exit proofs completed (exports audited + Stripe replay/refunds validated); keep all gates green**
* Next milestone after M2: **M3 Revenue Intelligence layer (start KPI contract hardening)**

## Runtime baseline

* Python: 3.12.3
* Framework: Django 5.2.10
* DB (dev): SQLite
* Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)

## Release gates (latest verified: 2026-01-19)

All gates below are required to remain green locally and in CI.

* `python manage.py check`: PASS
* `python manage.py test`: PASS (**50 tests**)
* `python manage.py run_checks --fail-on-issues`: PASS (**open=0, resolved=3**)
* `python manage.py makemigrations --check --dry-run`: PASS
* `python manage.py check --deploy`: PASS (prod-like settings)

  * Run with: `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`
* `ruff check .`: PASS
* `ruff format --check .`: PASS
* `pip-audit -r requirements.txt`: PASS (no known vulnerabilities)

### Important settings note (prevents false test failures)

* `purelaka.settings_prod` enables deployment protections such as `SECURE_SSL_REDIRECT=True`.
* If you run the test suite with `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`, Django’s test client will receive **301 redirects to [https://testserver/](https://testserver/)** for many endpoints.
* Therefore:

  * Run **tests and normal gates** with default settings (`purelaka.settings`).
  * Run **deploy gate only** with prod settings:

    * `DJANGO_SETTINGS_MODULE=purelaka.settings_prod python manage.py check --deploy`
  * After running the deploy gate in PowerShell, clear it:

    * `Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue`

> Note: PowerShell may show a `NativeCommandError` banner when piping/redirection is used (e.g., `Tee-Object`) even if the command succeeds. Treat `$LASTEXITCODE=0` as the authoritative success signal and keep outputs as proof.

## Notes (chronological)

* 2026-01-18: Monitoring namespace + smoke test stabilized; templates fixed to use namespaced URL reverse.
* 2026-01-19: CI confirmed green on main for core gates and engineering gates.
* 2026-01-19: RBAC regression resolved; roles service updated with deterministic role assignment for tests/support.
* 2026-01-19: Analytics exports hardened:

  * CSV exports protected by RBAC (ops/analyst/admin allowed; customer denied/hidden).
  * Export actions generate audit events (verified by tests).
  * Added export tests for CSV + audit expectations.
* 2026-01-19: Deploy gate made reproducible:

  * Introduced `purelaka/settings_prod.py` for `check --deploy` (prod-like toggles).
  * HSTS flags set to satisfy deploy checks in prod-like mode.
  * Confirmed that leaving `DJANGO_SETTINGS_MODULE` set to `settings_prod` causes test redirects (301); added policy to prevent confusion.
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
* 2026-01-19: Runbook updated with fresh install steps and local/CI gate parity (`docs/runbook.md`).

## Evidence (proof artifacts)

### M1 consolidated proof (authoritative)

* `docs/proof/m1_2026-01-19_full_gates.txt`

> Policy: prefer a single consolidated proof per milestone over many fragmented proof files.

### 2026-01-19 (additional M2 exit proofs)

* `docs/proof/analytics_export_orders_audit_2026-01-19.txt`
* `docs/proof/analytics_export_kpi_audit_2026-01-19.txt`
* `docs/proof/stripe_idempotency_2026-01-19.txt`
* `docs/proof/stripe_stock_idempotency_2026-01-19.txt`
* `docs/proof/stripe_refund_partial_2026-01-19.txt`
* `docs/proof/stripe_refund_full_2026-01-19.txt`

## Completed

### Milestone 1 — Audit-clean & runnable (complete)

* Wishlist included and wired (routes/templates/tests).
* Monitoring checks stable; negative-case proven (open → resolved workflow).
* Deterministic tests: pass with `PAYMENTS_USE_STRIPE=0`.
* Repo hygiene: `.env`, db, venv excluded; proofs stored under `docs/proof/`.
* CI established and green on main (quality + security gates).
* Deploy gate reproducible via `purelaka.settings_prod` and `check --deploy`.
* Full gate proof captured in `docs/proof/m1_2026-01-19_full_gates.txt`.

## In progress

### Milestone 2 — Operations Control hardened (in progress; exit criteria tightening)

* Order lifecycle rules enforced and tested (cancel/fulfill paths; access boundaries).
* Refund mapping updates order refund fields; reconciliation checks stable.
* Stock decrement/oversell prevention present; idempotent on webhook replay (proven).
* RBAC boundaries enforced across analytics/exports/monitoring/orders/payments.
* Audit logging present for operational actions; analytics exports audited (proven).
* Proof discipline: core gates are consolidated; targeted proofs added only when they defend a specific claim.

### Milestone 3 — Revenue Intelligence layer (partial)

* Snapshot system and KPI windows operational (7/30/90).
* Daily series charts operational.
* BI-ready exports present (CSV) with RBAC + audit expectations covered by tests.
* KPI definitions exist as a single source of truth and must remain aligned with implementation.

## Top blockers (max 3)

1. **KPI contract completeness:** `docs/kpi_definitions.md` must be the single source of truth for every KPI shown/exported and must match implementation.
2. **Buyer-grade packaging:** Docker/Postgres path not yet implemented (Milestone 4).
3. **Buyer due-diligence depth:** `docs/acceptance_matrix.md` and `docs/runbook.md` must remain current and fully trace claims → code/tests → proof.

## Next 3 actions (strict, step-by-step)

1. **KPI contract completeness (M3):** verify `docs/kpi_definitions.md` covers every KPI used in dashboard + snapshots + exports (definition, units, source, edge cases).
2. **Acceptance matrix expansion:** extend `docs/acceptance_matrix.md` to explicitly include Stripe replay idempotency, stock idempotency, refunds (partial/full), and export-audit proofs.
3. **M2 closeout discipline:** keep using “one authoritative proof per area” and avoid committing raw local artifacts (tmp JSON already ignored); ensure gates remain green after every change.
