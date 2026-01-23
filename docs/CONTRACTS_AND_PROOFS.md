# Contracts & Proof Index — Revenue Intelligence for Stripe Commerce

This document is the buyer-facing index that maps:
- contracts (what we promise)
- tests (what enforces it)
- proof artifacts (what was captured)

Policy:
- If a claim/contract is not linked here, it is not part of the buyer-ready proof pack.
- Any change to a contract requires: update contract doc/JSON + update/add a test + update `docs/STATUS.md`.
- Proof files must be reproducible from scripts/commands below and stored under `docs/proof/`.

## Buyer entry point (start here)

To verify the buyer-ready deployment baseline (Milestone 4 closure), review these proof artifacts in order:

1) **M4.6 final baseline gates (authoritative):**
   - `docs/proof/m4_2026-01-23_m46_final_baseline_full_gates.txt`

2) **M4.6 host full release gates (default settings; fresh capture on 2026-01-23):**
   - `docs/proof/m4_2026-01-23_m46_host_full_gates_default.txt`

3) **Index update verification (confirms indexes updated correctly):**
   - `docs/proof/m4_2026-01-23_m46_index_update_docs_gates.txt`

4) **Post-close confirmation (final “after everything” verification):**
   - `docs/proof/m4_2026-01-23_m46_post_close_docs_index_gates.txt`

The milestone closure date and current status are recorded in `docs/STATUS.md`.

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

### Deployment parity contract (buyer-ready runtime baseline)
- Postgres parity: app must run, migrate, and pass gates on Postgres, not only SQLite.
- Containerization baseline: Dockerfile + Docker Compose must build and run with Postgres.
- Teardown reliability: Postgres test DB teardown must be deterministic (no lingering session failures).

### Health / readiness contract
- Endpoint: `GET /monitoring/healthz/`
- Behavior:
  - Returns **200** when the service is ready (default DB reachable; `SELECT 1` succeeds)
  - Returns **503** when the service is not ready (default DB unreachable)
- Enforced by:
  - `monitoring/tests/test_healthz.py`

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

### M4 — deployment baseline proofs (complete through M4.4 Step 3)

Postgres parity + containerization baseline:

- `docs/proof/m4_2026-01-21_postgres_parity_gates.txt` — Postgres parity gates (local Docker Compose + `purelaka.settings_postgres`)
- `docs/proof/m4_2026-01-22_dockerfile_gate.txt` — Dockerfile baseline (build + gates)
- `docs/proof/m4_2026-01-22_compose_web_db_parity_gates.txt` — Docker Compose web+db parity gates (gates executed inside the app container; confirms `vendor=postgresql`, `host=db`, `name=purelaka`)
- `docs/proof/m4_2026-01-22_docs_index_gates.txt` — Docs/index gates proof after updating `docs/STATUS.md` + `docs/CONTRACTS_AND_PROOFS.md`
- `docs/proof/m4_2026-01-22_post_index_full_gates.txt` — Post-index full gates snapshot (authoritative “after docs updates” confirmation)
- `docs/proof/m4_2026-01-22_contracts_proofs_update_gates.txt` — Gates snapshot after updating contracts/proofs index (docs-only change verification)
- `docs/proof/m4_2026-01-22_contracts_proofs_indexed_gates.txt` — Gates snapshot after indexing the previous proof into this document (index completeness verification)
- `docs/proof/m4_2026-01-22_full_gates_after_docs_sync.txt` — Full gates snapshot after docs sync on `main`
- `docs/proof/m4_2026-01-22_full_gates_indexed_gates.txt` — Gates snapshot after indexing the previous full-gates proof into `docs/STATUS.md` + `docs/CONTRACTS_AND_PROOFS.md`
- `docs/proof/m4_2026-01-22_healthz_gunicorn_gates.txt` — M4.4 Step 1: health/readiness endpoint + gunicorn dependency; gates + manual readiness response captured
- `docs/proof/m4_2026-01-22_gunicorn_runtime_smoke.txt` — M4.4 Step 2: container serves via Gunicorn (WSGI); `/monitoring/healthz/` returns 200 and shows `Server: gunicorn`
- `docs/proof/m4_2026-01-22_gunicorn_compose_web_db_parity_gates.txt` — M4.4 Step 2: compose parity gates executed inside container under Gunicorn runtime (includes pip-audit result)
- `docs/proof/m4_2026-01-22_docs_cleanup_gates.txt` — Docs cleanup gates proof (normalizes docs formatting; verifies gates remain green)

Prod-like compose (production-shaped container runtime):

- `docs/proof/m4_2026-01-22_prod_compose_deploy_gate.txt` — M4.4 Step 3: prod compose deploy gate (`python manage.py check --deploy`) executed inside container (`DJANGO_SETTINGS_MODULE=purelaka.settings_prod`)
- `docs/proof/m4_2026-01-22_prod_compose_healthz_ipv4_smoke.txt` — M4.4 Step 3: prod compose host smoke (IPv4; Windows-safe; confirms `Server: gunicorn`)
- `docs/proof/m4_2026-01-22_prod_compose_healthz_redirect_headers.txt` — M4.4 Step 3: redirect/header capture for host healthz smoke (documents 301/host behaviour under prod flags)
- `docs/proof/m4_2026-01-22_prod_compose_healthz_smoke.txt` — M4.4 Step 3: initial prod compose host healthz smoke capture (raw output)
- `docs/proof/m4_2026-01-22_gunicorn_server_header_proof.txt` — M4.4 Step 3: Gunicorn `Server:` header proof (sanity confirmation)
- `docs/proof/m4_2026-01-22_prod_compose_full_gates.txt` — M4.4 Step 3: prod compose full gates executed inside container (initial capture; may contain failures prior to `settings_prod` redirect fix)
- `docs/proof/m4_2026-01-22_prod_compose_deploy_gate_after_settings_prod_fix.txt` — M4.4 Step 3: deploy gate re-captured after `settings_prod` test-redirect fix (authoritative deploy proof after fix)
- `docs/proof/m4_2026-01-22_prod_compose_full_gates_after_settings_prod_fix.txt` — M4.4 Step 3: full gates re-captured after `settings_prod` test-redirect fix (authoritative Step 3 PASS proof)
- `docs/proof/m4_2026-01-22_after_fix_docs_index_gates.txt` — M4.4 Step 3: docs/index gates after re-indexing the after-fix proofs (index completeness verification)
- `docs/proof/m4_2026-01-22_prod_compose_full_gates_rerun_clean.txt` — M4.4 Step 3: prod compose full gates re-run from clean rebuild (authoritative rerun proof)
- `docs/proof/m4_2026-01-22_prod_compose_rerun_docs_index_gates.txt` — Docs/index gates after indexing rerun proofs (docs-only change verification)
- `docs/proof/m4_2026-01-22_prod_compose_ipv4_docs_index_gates.txt` — Gates snapshot after indexing prod compose IPv4 smoke proof into docs (index completeness verification)
- `docs/proof/m4_2026-01-22_m45_status_next_step_docs_index_gates.txt` — Docs/index gates after adding M4.5 next step line in STATUS (docs-only change verification)
- `docs/proof/m4_2026-01-22_m45_prod_compose_host_healthz_headers_200.txt` — M4.5: prod compose host healthz headers (200 OK; confirms `Server: gunicorn` + security headers)
- `docs/proof/m4_2026-01-22_m45_prod_compose_full_gates.txt` — M4.5: prod compose full gates run (in-container; verifies deploy + tests + run_checks + ruff + pip-audit under prod compose)
- `docs/proof/m4_2026-01-22_m45_full_gates_after_updates.txt` — M4.5: full gates snapshot after M4.5 updates (authoritative “after updates” baseline)
- `docs/proof/m4_2026-01-22_m45_docs_index_gates_after_updates.txt` — Docs/index gates after indexing M4.5 full-gates proofs (docs-only change verification)
- `docs/proof/m4_2026-01-22_m45_complete_status_docs_index_gates.txt` — Docs/index gates after marking M4.5 complete and adding the next-step line (docs-only change verification)
- `docs/proof/m4_2026-01-22_m46_status_next_step_docs_index_gates.txt` — Docs/index gates after setting M4.6 as current step in STATUS (docs-only change verification)

M4.6 closure proofs:

- `docs/proof/m4_2026-01-23_m46_final_baseline_full_gates.txt` — M4.6 final baseline full gates (authoritative closure proof)
- `docs/proof/m4_2026-01-23_m46_host_full_gates_default.txt` — M4.6 host full release gates (default settings; fresh capture on 2026-01-23)
- `docs/proof/m4_2026-01-23_m46_index_update_docs_gates.txt` — M4.6 index update gates (proof indexing verification)
- `docs/proof/m4_2026-01-23_m46_post_close_docs_index_gates.txt` — M4 post-close docs/index gates (final confirmation)

## 4) How to re-verify (buyer due-diligence commands)

Core gates (single consolidated proof):
- `.\scripts\gates.ps1 -ProofPath "docs/proof/m3_2026-01-21_full_gates_clean.txt"`

Postgres parity gates (local, host-run using Postgres settings):
- `DJANGO_SETTINGS_MODULE=purelaka.settings_postgres .\scripts\gates.ps1 -ProofPath "docs/proof/m4_2026-01-21_postgres_parity_gates.txt"`

Docker Compose parity gates (web+db; run gates inside the app container):
- `docker compose up -d --build`
- `docker exec -i purelaka_web sh -lc "python manage.py check && python manage.py test --noinput && python manage.py run_checks --fail-on-issues && python manage.py makemigrations --check --dry-run && ruff check . && ruff format --check . && pip-audit -r requirements.txt" > docs/proof/m4_2026-01-22_compose_web_db_parity_gates.txt`

Or run individually:
- `python manage.py check`
- `python manage.py test --noinput`
- `python manage.py run_checks --fail-on-issues`
- `python manage.py makemigrations --check --dry-run`
- `ruff check .`
- `ruff format --check .`
- `pip-audit -r requirements.txt`

Deploy gate (prod-like, self-auditing proof):
- `powershell -ExecutionPolicy Bypass -File scripts/deploy_gate.ps1`
- `Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue`
