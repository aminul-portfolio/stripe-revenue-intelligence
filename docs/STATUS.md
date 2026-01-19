# STATUS — Revenue Intelligence for Stripe Commerce

## Current milestone

- Milestone: **M2 Operations Control hardened (in progress)**
- Current step: **Close M2 proof discipline and RBAC/audit coverage; keep all gates green**
- Next milestone after M2: **M3 Revenue Intelligence layer (in progress / expanding)**

## Runtime baseline

- Python: 3.12.3
- Framework: Django 5.2.10
- DB (dev): SQLite
- Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)

## Release gates (latest verified: 2026-01-19)

All gates below are required to remain green locally and in CI.

- `python manage.py check`: PASS
- `python manage.py test`: PASS (**50 tests**)
- `python manage.py run_checks --fail-on-issues`: PASS (**open=0, resolved=3**)
- `python manage.py makemigrations --check --dry-run`: PASS
- `python manage.py check --deploy`: PASS (prod-like settings)
  - Run with: `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`
- `ruff check .`: PASS
- `ruff format --check .`: PASS
- `pip-audit -r requirements.txt`: PASS (no known vulnerabilities)

### Important settings note (prevents false test failures)

- `purelaka.settings_prod` enables deployment protections such as `SECURE_SSL_REDIRECT=True`.
- If you run the test suite with `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`, Django’s test client will receive **301 redirects to https://testserver/** for many endpoints.
- Therefore:
  - Run **tests and normal gates** with default settings (`purelaka.settings`).
  - Run **deploy gate only** with prod settings:
    - `DJANGO_SETTINGS_MODULE=purelaka.settings_prod python manage.py check --deploy`
  - After running the deploy gate in PowerShell, clear it:
    - `Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue`

> Note: PowerShell may show a `NativeCommandError` banner when piping/redirection is used (e.g., `Tee-Object`) even if the command succeeds. Treat `$LASTEXITCODE=0` as the authoritative success signal and keep outputs as proof.

## Notes (chronological)

- 2026-01-18: Monitoring namespace + smoke test stabilized; templates fixed to use namespaced URL reverse.
- 2026-01-19: CI confirmed green on main for core gates and engineering gates.
- 2026-01-19: RBAC regression resolved; roles service updated with deterministic role assignment for tests/support.
- 2026-01-19: Analytics exports hardened:
  - CSV exports protected by RBAC (ops/analyst/admin allowed; customer denied/hidden)
  - Export actions generate audit events (verified by tests)
  - Added export tests for CSV + audit expectations
- 2026-01-19: Deploy gate made reproducible:
  - Introduced `purelaka/settings_prod.py` for `check --deploy` (prod-like toggles)
  - HSTS flags set to satisfy deploy checks in prod-like mode
  - Confirmed that leaving `DJANGO_SETTINGS_MODULE` set to `settings_prod` causes test redirects (301); added policy to prevent confusion.
- 2026-01-19: Migration drift fixed:
  - Added `orders/migrations/0005_alter_order_status.py`
  - `makemigrations --check --dry-run` now clean

## Evidence (proof artifacts)

### M1 consolidated proof (authoritative)
- `docs/proof/m1_2026-01-19_full_gates.txt`

> Policy: prefer a single consolidated proof per milestone over many fragmented proof files.

## Completed

### Milestone 1 — Audit-clean & runnable (complete)

- Wishlist included and wired (routes/templates/tests)
- Monitoring checks stable; negative-case proven (open → resolved workflow)
- Deterministic tests: pass with `PAYMENTS_USE_STRIPE=0`
- Repo hygiene: `.env`, db, venv excluded; proofs stored under `docs/proof/`
- CI established and green on main (quality + security gates)
- Deploy gate reproducible via `purelaka.settings_prod` and `check --deploy`
- Full gate proof captured in `docs/proof/m1_2026-01-19_full_gates.txt`

## In progress

### Milestone 2 — Operations Control hardened

- Order lifecycle rules enforced and tested (keep expanding coverage as features are added)
- Refund mapping and reconciliation checks present; monitoring remains green
- Stock decrement/oversell prevention present (ensure concurrency coverage is preserved)
- RBAC boundaries enforced across analytics/exports/monitoring/orders/payments
- Audit logging present for operational actions; exports now audited

### Milestone 3 — Revenue Intelligence layer (partial)

- Snapshot system and KPI windows operational (7/30/90)
- Daily series charts operational
- BI-ready exports present (CSV) with RBAC + audit expectations covered by tests

## Top blockers (max 3)

1. **KPI contract completeness:** `docs/kpi_definitions.md` must be the single source of truth for every KPI shown, and must match implementation.
2. **Buyer-grade packaging:** Docker/Postgres path not yet implemented (Milestone 4).
3. **Buyer due-diligence docs:** need `docs/acceptance_matrix.md` + `docs/runbook.md` to make claims defensible for sale.

## Next 3 actions (strict, step-by-step)

1. **KPI definitions (M3):** create/complete `docs/kpi_definitions.md` and cross-check against dashboard + snapshot fields.
2. **RBAC matrix + acceptance mapping (Overlay A):** add `docs/rbac_matrix.md` and begin `docs/acceptance_matrix.md` mapping claims → code → tests → demo steps.
3. **Runbook skeleton (Overlay D/E):** add `docs/runbook.md` with “fresh install” steps and the exact gate commands (local + CI).
