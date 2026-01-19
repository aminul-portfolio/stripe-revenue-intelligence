# STATUS — Revenue Intelligence for Stripe Commerce

## Current milestone

* Milestone: **M3 Revenue Intelligence layer (in progress)**
* Current step: **M3.2 Security baseline + CI hygiene proven (settings/.env.example + security headers test + proofs captured)**

## Runtime baseline

* Python: 3.12.3
* DB (dev): SQLite
* Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)

## Gates (latest: 2026-01-19)

* `python manage.py check`: PASS
* `python manage.py test`: PASS (**44 tests**)
* `python manage.py run_checks --fail-on-issues`: PASS (**open=0, resolved=3**)
* `python manage.py makemigrations --check --dry-run`: PASS *(via CI)*
* `python manage.py check --deploy`: PASS *(via CI / prod-like settings mode)*
* `ruff check .`: PASS
* `ruff format --check .`: PASS *(after `ruff format .` on 2026-01-19)*
* `pip-audit -r requirements.txt`: PASS *(no known vulnerabilities)*

> Note: PowerShell may print a `NativeCommandError` banner when piping/redirection is used (e.g., `Tee-Object`) even if the command succeeds. Treat `$LASTEXITCODE=0` as the authoritative success signal; keep the output as proof.

## Notes (chronological)

* 2026-01-18: Monitoring namespace + smoke test stabilized; templates fixed to use namespaced URL reverse.
* 2026-01-18: Per-app proofs added (payments/orders/monitoring/accounts/analyticsapp/wishlist); tracker assets committed.
* 2026-01-18: Wishlist tests made discoverable (added `wishlist/tests/__init__.py` + smoke tests).
* 2026-01-19: Stripe live smoke executed successfully using Stripe CLI (manual, local):

  * Webhook listener forwarded to `/payments/webhook/`
  * Events observed as HTTP 200 (created/succeeded/charge/mandate updates)
  * Latest order verified as `paid` with `stripe_payment_intent` and `stripe_charge_id`
  * Secrets redacted in proof notes
* 2026-01-19: CI pipeline confirmed green (ruff check, ruff format check, system check, migrations check, tests, run_checks, pip-audit).
* 2026-01-19: Formatting fix applied (`ruff format .`) and pushed; CI remains green.
* 2026-01-19: Security baseline introduced and documented:

  * `settings.py` supports `DJANGO_SECRET_KEY` or `SECRET_KEY` (dev fallback only)
  * Stripe env validation enforced only when `PAYMENTS_USE_STRIPE=1`
  * Security headers/cookie flags/HSTS toggled automatically by `DEBUG`
  * `core.context_processors.payments_flags` wired into templates
  * Added `core/tests/test_security_headers.py` (smoke)
* 2026-01-19: Status spelling normalization completed for active code and docs:

  * Canonical spelling: **canceled**
  * Legacy spelling allowed only in historical narrative and/or old migrations; active code/tests/docs use canonical spelling.

## Evidence (proof artifacts)

### 2026-01-18 (M2 proofs)

* `docs/proof/m2_2026-01-18_check.txt`
* `docs/proof/m2_2026-01-18_run_checks.txt`
* `docs/proof/m2_2026-01-18_test_payments.txt`
* `docs/proof/m2_2026-01-18_test_orders.txt`
* `docs/proof/m2_2026-01-18_test_monitoring.txt`
* `docs/proof/m2_2026-01-18_test_accounts.txt`
* `docs/proof/m2_2026-01-18_test_analyticsapp.txt`
* `docs/proof/m2_2026-01-18_test_wishlist.txt`
* `docs/proof/m2_2026-01-18_monitoring_template_hits.txt`

### 2026-01-19 (CI + security + Stripe live smoke)

* `docs/proof/m2_2026-01-19_ci_green.txt`

* `docs/proof/m2_2026-01-19_tests.txt`

* `docs/proof/m2_2026-01-19_run_checks.txt`

* `docs/proof/m2_2026-01-19_ruff_check.txt`

* `docs/proof/m2_2026-01-19_ruff_format_check.txt`

* `docs/proof/m2_2026-01-19_pip_audit.txt`

* `docs/proof/m3_2026-01-19_check.txt`

* `docs/proof/m3_2026-01-19_tests.txt`

* `docs/proof/m3_2026-01-19_run_checks.txt`

* `docs/proof/m3_2026-01-19_ruff_check.txt`

* `docs/proof/m3_2026-01-19_ruff_format_check.txt`

* `docs/proof/m3_2026-01-19_pip_audit.txt`

* `docs/proof/m3_2026-01-19_tests_2.txt`

* `docs/proof/m3_2026-01-19_ruff_check_2.txt`

* `docs/proof/m3_2026-01-19_ruff_format_check_2.txt`

* `docs/proof/m3_2026-01-19_pip_audit_2.txt`

* `docs/proof/m3_2026-01-19_migrate_canceled_fix.txt`

* `docs/proof/m3_2026-01-19_tests_canceled_fix.txt`

* `docs/proof/m3_2026-01-19_run_checks_canceled_fix.txt`

* `docs/proof/m3_2026-01-19_ruff_check_canceled_fix.txt`

* `docs/proof/m3_2026-01-19_ruff_format_canceled_fix.txt`

* `docs/proof/m3_2026-01-19_pip_audit_canceled_fix.txt`

* `docs/proof/stripe_live_2026-01-19_notes.txt`

* `docs/stripe_live_smoke_checklist.md`

* `docs/security.md`

## Completed

### Milestone 1 — Audit-clean & runnable

* Wishlist included and wired (routes/templates/tests)
* Monitoring checks stable; negative-case proven (open → resolved workflow)
* StripeEvent correctness + idempotency boundary validated by tests
* Deterministic tests: pass with `PAYMENTS_USE_STRIPE=0`
* Repo hygiene: `.env`, db, venv excluded; proofs stored under `docs/proof/`
* CI established and green on main (quality + security gates)

### Milestone 2 — Operations Control hardened

* Order lifecycle rules enforced and tested
* Refund mapping updates order refund fields; reconciliation checks stable
* Stock decrement on payment success (oversell prevention via transactional locking)
* RBAC boundaries enforced across analytics/exports/monitoring/orders/payments
* Monitoring UI endpoints exist and are protected; URL namespace fixed
* Audit logging present for key operational actions (per existing implementation)

### Milestone 3 — Revenue Intelligence layer (partial)

* Snapshot system and KPIs operational (7/30/90 windows, daily series)
* Wishlist-to-purchase funnel metric integrated into snapshot KPIs
* Security baseline added (headers/cookies/HSTS toggling; deploy-friendly defaults)

## Top blockers (max 3)

1. **KPI contract completeness:** `docs/kpi_definitions.md` must be the single source of truth for every KPI shown (and match implementation).
2. **Buyer-grade packaging gap:** Docker/Postgres path not yet implemented (Milestone 4 dependency).
3. **Acceptance matrix/runbook gap:** need `docs/acceptance_matrix.md` + `docs/runbook.md` to make claims defensible for sale.

## Next 3 actions

1. **KPI definitions (M3.1):** create/complete `docs/kpi_definitions.md` and cross-check against dashboard + snapshot fields.
2. **Exports + audit (M3.3):** ensure exports are BI-ready (stable headers), RBAC-protected, and generate audit events; capture sample export proof.
3. **Milestone 4 scaffolding plan:** draft Docker Compose (web + db + redis) and a deployment checklist, but do not implement until M3 deliverables are stable.
