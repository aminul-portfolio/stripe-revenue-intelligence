# Contracts & Proof Index — Revenue Intelligence for Stripe Commerce

This document is the buyer-facing index that maps:
- contracts (what we promise)
- tests (what enforces it)
- proof artifacts (what was captured)

Policy:
- If a claim/contract is not linked here, it is not part of the buyer-ready proof pack.
- Any change to a contract requires: update contract doc/JSON + update/add a test + update `docs/STATUS.md`.
- Proof files must be reproducible from scripts/commands below and stored under `docs/proof/`.

## 1) Contracts (what we promise)

### KPI meaning contract
- `docs/kpi_definitions.md`
  - Defines KPI meaning, windows (7/30/90), boundaries, sources, and edge cases.
  - Must remain aligned with the export header contract (`docs/contracts/kpi_contract.json`).

KPI contract completeness proof (M3):
- `docs/proof/m3_kpi_contract_completeness_2026-01-21.txt`
  - Confirms every header in `docs/contracts/kpi_contract.json` is defined in `docs/kpi_definitions.md`.

### Export schema contract (machine-checkable)
- `docs/contracts/kpi_contract.json`
  - Authoritative list of export headers per export type.
  - Prevents silent schema drift.

### RBAC contract (roles + access rules)
- `docs/rbac_matrix.md`
  - Source of truth for role-based access; tests must enforce.

### Stock & concurrency contract (payments + inventory)
- Prevent double-decrement on Stripe webhook replay (idempotent handler boundary).
- Prevent negative stock (oversell raises `StockOversellError` and does not mark order paid).
- Concurrency safety: stock decrement uses row locks (`select_for_update`) to prevent race-condition double-decrement.

### Acceptance matrix (product claims → code/tests/proofs)
- `docs/acceptance_matrix.md`
  - Buyer claim inventory. If it is not here, it is not shipped.

## 2) Tests that enforce the contracts

### Export schema drift control
- `analyticsapp/tests/test_export_contract.py`
  - Validates CSV export headers match `docs/contracts/kpi_contract.json`.

### RBAC surface protection (contract-level)
- `accounts/tests/test_rbac_surface_contract.py`
  - Prevents accidental exposure of protected analytics/exports/monitoring surfaces.
  - Uses namespaced monitoring URL reverse: `reverse("monitoring:monitoring-issues")`.

### Payments stock idempotency (handler boundary)
- `payments/tests/test_payment_intent_stock_idempotency.py`
  - Proves `payment_intent.succeeded` handler decrements stock once and is replay-safe:
    - product stock path
    - variant stock path
    - preorder skip path

### Stock concurrency protection (locking boundary)
- `payments/tests/test_stock_concurrency.py`
  - Proves row-locking prevents double-decrement under contention (TransactionTestCase).

### Postgres teardown stability (parity reliability)
- `purelaka/test_runner.py`
  - Ensures Postgres test DB teardown is reliable by terminating lingering sessions before drop.
  - Prevents nondeterministic `database ... is being accessed by other users` failures on Docker/WSL.

### Core RBAC coverage (existing suite)
- `accounts/tests/test_rbac_views.py`
- `analyticsapp/tests/test_access.py`
- `analyticsapp/tests/test_exports_csv.py`
- `analyticsapp/tests/test_exports_csv_audit.py`
- `orders/tests/test_order_access.py`
- `orders/tests/test_ops_endpoints.py`
- `orders/tests/test_payment_start_access.py`

## 3) Proof artifacts (what was captured)

### M1 — consolidated gates proof (authoritative)
- `docs/proof/m1_2026-01-19_full_gates.txt`

### M2 — exit proofs (authoritative set)

Stripe safety + refunds:
- `docs/proof/stripe_idempotency_2026-01-19.txt`
- `docs/proof/stripe_stock_idempotency_2026-01-19.txt`
- `docs/proof/stripe_refund_partial_2026-01-19.txt`
- `docs/proof/stripe_refund_full_2026-01-19.txt`

Exports audited (attachments + audit events):
- `docs/proof/analytics_export_orders_audit_2026-01-19.txt`
- `docs/proof/analytics_export_kpi_audit_2026-01-19.txt`
- `docs/proof/analytics_export_customers_audit_2026-01-19.txt`
- `docs/proof/analytics_export_products_audit_2026-01-20.txt`

### M3 — contracts + hardening proofs

Export contract enforcement:
- `docs/proof/m3_export_contract_tests_2026-01-20.txt`
- `docs/proof/m3_export_contract_test_verbose_2026-01-20.txt`
- `docs/proof/m3_kpi_contract_alignment_2026-01-20.txt`
- `docs/proof/m3_kpi_inventory_2026-01-20.txt`
- `docs/proof/m3_kpi_contract_completeness_2026-01-21.txt`
- `docs/proof/m3_kpi_parity_inventory_2026-01-21.txt`

Payments hardening proof:
- `docs/proof/m3_payment_intent_stock_idempotency_tests_2026-01-21.txt`
- `docs/proof/m3_stock_oversell_prevention_tests_2026-01-21.txt`

Stock concurrency proof:
- `docs/proof/m3_stock_concurrency_2026-01-21.txt`

Gates + deploy verification (authoritative):
- `docs/proof/m3_2026-01-21_full_gates_clean.txt`
- `docs/proof/m3_deploy_gate_2026-01-21.txt`
  - Includes timestamp + `DJANGO_SETTINGS_MODULE` + env-cleared confirmation.
- `scripts/gates.ps1`
- `scripts/deploy_gate.ps1`

Acceptance matrix snapshot:
- `docs/proof/m3_acceptance_matrix_2026-01-20.txt`

RBAC surface contract proof:
- `docs/proof/m3_rbac_surface_contract_2026-01-20.txt`

### M4 — deployment baseline proofs (in progress)

Postgres parity gates:
- `docs/proof/m4_2026-01-21_postgres_parity_gates.txt` — Postgres parity gates (local Docker Compose + `purelaka.settings_postgres`)
- `docs/proof/m4_2026-01-22_dockerfile_gate.txt` — Dockerfile baseline (build + gates)

## 4) How to re-verify (buyer due-diligence commands)

Core gates (single consolidated proof):
- `.\scripts\gates.ps1 -ProofPath "docs/proof/m3_YYYY-MM-DD_full_gates_clean.txt"`

Postgres parity gates (local Docker Compose):
- `DJANGO_SETTINGS_MODULE=purelaka.settings_postgres .\scripts\gates.ps1 -ProofPath "docs/proof/m4_YYYY-MM-DD_postgres_parity_gates.txt"`

Or run individually:
- `python manage.py check`
- `python manage.py test`
- `python manage.py run_checks --fail-on-issues`
- `python manage.py makemigrations --check --dry-run`
- `ruff check .`
- `ruff format --check .`
- `pip-audit -r requirements.txt`

Deploy gate (prod-like, self-auditing proof):
- `powershell -ExecutionPolicy Bypass -File scripts/deploy_gate.ps1`
- `Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue`
