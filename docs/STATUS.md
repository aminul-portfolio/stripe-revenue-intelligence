# STATUS — Revenue Intelligence for Stripe Commerce

## Current milestone

* Milestone: **M4 Deployment baseline (in progress)**
* Current step: **M4.4 Production-shaped container baseline (Step 3: prod-like compose baseline) (complete)**
* M3 closed: **2026-01-21** (exit proofs complete; gates verified)

## Runtime baseline

* Python: 3.12.3
* Framework: Django 5.2.10
* DB (dev): SQLite
* Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)
* Postgres parity settings: `DJANGO_SETTINGS_MODULE=purelaka.settings_postgres`
* Container baseline: Dockerfile + Docker Compose (`docker-compose.yml`, `docker-compose.prod.yml`)

## Release gates (latest verified: 2026-01-22)

All gates below must remain green locally and in CI.

* `python manage.py check`: PASS
* `python manage.py test`: PASS (**63 tests**, see latest proof)
* `python manage.py run_checks --fail-on-issues`: PASS (**open=0, resolved=3**, see latest proof)
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
  * Run **tests and normal gates** with default settings (`purelaka.settings`), or Postgres parity settings (`purelaka.settings_postgres`).
  * Run **deploy gate only** with prod settings:
    * `DJANGO_SETTINGS_MODULE=purelaka.settings_prod python manage.py check --deploy`
  * After running the deploy gate in PowerShell, clear it:
    * `Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue`

> Note: PowerShell may show a `NativeCommandError` banner when piping/redirection is used (e.g., `Tee-Object`) even if the command succeeds. Treat `$LASTEXITCODE=0` as the authoritative success signal and keep outputs as proof.

## Notes (chronological)

* 2026-01-22: **M4.4 Step 3 prod compose deploy gate re-captured after settings_prod test-redirect fix:** `docs/proof/m4_2026-01-22_prod_compose_deploy_gate_after_settings_prod_fix.txt`.
* 2026-01-22: **M4.4 Step 3 prod compose full gates re-captured after settings_prod test-redirect fix (authoritative):** `docs/proof/m4_2026-01-22_prod_compose_full_gates_after_settings_prod_fix.txt`.
* 2026-01-22: **M4.4 Step 3 prod compose full gates captured (prod-like runtime):** `docs/proof/m4_2026-01-22_prod_compose_full_gates.txt`.
* 2026-01-22: **M4.4 Step 3 prod compose PID1 cmdline captured (Gunicorn is PID1):** `docs/proof/m4_2026-01-22_prod_compose_pid1_cmdline.txt`.
* 2026-01-22: **M4.4 Step 3 Gunicorn server header proof captured (in-container):** `docs/proof/m4_2026-01-22_gunicorn_server_header_proof.txt`.
* 2026-01-22: **M4 prod compose (IPv4) docs/index gates captured:** `docs/proof/m4_2026-01-22_prod_compose_ipv4_docs_index_gates.txt`.
* 2026-01-22: **M4 prod compose host smoke (IPv4) captured:** `docs/proof/m4_2026-01-22_prod_compose_healthz_ipv4_smoke.txt` (Windows-safe; confirms `Server: gunicorn`).
* 2026-01-22: **M4 prod compose deploy gate captured:** `docs/proof/m4_2026-01-22_prod_compose_deploy_gate.txt` (`python manage.py check --deploy` executed inside container).
* 2026-01-22: **Docs cleanup gates captured:** `docs/proof/m4_2026-01-22_docs_cleanup_gates.txt`.
* 2026-01-22: **M4.4 Step 2 Gunicorn container runtime proven:** `docs/proof/m4_2026-01-22_gunicorn_runtime_smoke.txt` + `docs/proof/m4_2026-01-22_gunicorn_compose_web_db_parity_gates.txt`.
* 2026-01-22: **M4.4 Step 1 healthz + gunicorn dependency proven:** `docs/proof/m4_2026-01-22_healthz_gunicorn_gates.txt`.
* 2026-01-22: **M4 full gates indexed gates captured:** `docs/proof/m4_2026-01-22_full_gates_indexed_gates.txt`.
* 2026-01-22: Docs notes chronology updated; gates captured: `docs/proof/m4_2026-01-22_notes_update_gates.txt`.
* 2026-01-22: **M4 full gates after docs sync captured:** `docs/proof/m4_2026-01-22_full_gates_after_docs_sync.txt`.
* 2026-01-22: **M4 post-index full gates snapshot captured:** `docs/proof/m4_2026-01-22_post_index_full_gates.txt`.
* 2026-01-22: **M4 docs/index gates captured after updating proof pack:** `docs/proof/m4_2026-01-22_docs_index_gates.txt`.
* 2026-01-22: **M4.3 Docker Compose web+db parity gates captured:** `docs/proof/m4_2026-01-22_compose_web_db_parity_gates.txt`.
* 2026-01-22: **M4.3 docker-compose updated to include `web` service** (app container + Postgres) and parity proven from inside the container.
* 2026-01-22: **M4.2 Dockerfile gate captured:** `docs/proof/m4_2026-01-22_dockerfile_gate.txt`.

* 2026-01-21: **M4.1 Postgres parity gates captured:** `docs/proof/m4_2026-01-21_postgres_parity_gates.txt`.
* 2026-01-21: Payments hardening proof captured: stock idempotency tests (`docs/proof/m3_payment_intent_stock_idempotency_tests_2026-01-21.txt`).
* 2026-01-21: Stock concurrency test added and proof captured (`docs/proof/m3_stock_concurrency_2026-01-21.txt`).
* 2026-01-21: Deploy gate proof upgraded to be self-auditing (timestamp + `DJANGO_SETTINGS_MODULE` + env-cleared confirmation).
* 2026-01-21: Consolidated M3 gates proof captured as a buyer-ready snapshot (`docs/proof/m3_2026-01-21_full_gates_clean.txt`).
* 2026-01-21: Payments hardening proof captured: oversell prevention tests (`docs/proof/m3_stock_oversell_prevention_tests_2026-01-21.txt`).
* 2026-01-21: Milestone 3 hardening closed (contracts + proofs + gates green).

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

### M3 proof pack (authoritative)

Buyer entry point: `docs/CONTRACTS_AND_PROOFS.md`

Consolidated M3 gates proof (authoritative):

* `docs/proof/m3_2026-01-21_full_gates_clean.txt`
* `docs/proof/m3_deploy_gate_2026-01-21.txt`

Key M3 hardening proofs (2026-01-21):

* `docs/proof/m3_payment_intent_stock_idempotency_tests_2026-01-21.txt`
* `docs/proof/m3_stock_oversell_prevention_tests_2026-01-21.txt`
* `docs/proof/m3_stock_concurrency_2026-01-21.txt`
* `docs/proof/m3_kpi_parity_inventory_2026-01-21.txt`
* `docs/proof/m3_kpi_contract_completeness_2026-01-21.txt`

### M4 proof pack (in progress)

* `docs/proof/m4_2026-01-22_prod_compose_deploy_gate_after_settings_prod_fix.txt` — M4.4 Step 3: deploy gate re-captured after `settings_prod` test-redirect fix (authoritative deploy proof after fix)
* `docs/proof/m4_2026-01-22_prod_compose_full_gates_after_settings_prod_fix.txt` — M4.4 Step 3: full gates re-captured after `settings_prod` test-redirect fix (authoritative Step 3 PASS proof)
* `docs/proof/m4_2026-01-21_postgres_parity_gates.txt` — Postgres parity gates (Docker Compose + `purelaka.settings_postgres`)
* `docs/proof/m4_2026-01-22_dockerfile_gate.txt` — Dockerfile build + gates verification
* `docs/proof/m4_2026-01-22_compose_web_db_parity_gates.txt` — Docker Compose web+db parity gates (gates executed inside app container; confirms Postgres `db` host)
* `docs/proof/m4_2026-01-22_docs_index_gates.txt` — Docs/index gates proof after updating `docs/STATUS.md` + `docs/CONTRACTS_AND_PROOFS.md`
* `docs/proof/m4_2026-01-22_post_index_full_gates.txt` — Post-index full gates snapshot (authoritative “after docs updates” confirmation)
* `docs/proof/m4_2026-01-22_contracts_proofs_update_gates.txt` — Gates snapshot after updating contracts/proofs index (docs-only change verification)
* `docs/proof/m4_2026-01-22_contracts_proofs_indexed_gates.txt` — Gates snapshot after indexing the previous proof into the index (index completeness verification)
* `docs/proof/m4_2026-01-22_full_gates_after_docs_sync.txt` — Full gates snapshot after docs sync on `main` (authoritative current baseline)
* `docs/proof/m4_2026-01-22_full_gates_indexed_gates.txt` — Gates snapshot after indexing the previous full-gates proof into the docs
* `docs/proof/m4_2026-01-22_healthz_gunicorn_gates.txt` — M4.4 Step 1: health/readiness endpoint (`/monitoring/healthz/`) + gunicorn dependency; gates + manual check captured
* `docs/proof/m4_2026-01-22_gunicorn_runtime_smoke.txt` — M4.4 Step 2: Gunicorn runtime smoke (healthz shows `Server: gunicorn`)
* `docs/proof/m4_2026-01-22_gunicorn_compose_web_db_parity_gates.txt` — M4.4 Step 2: compose web+db parity gates under Gunicorn runtime (in-container gates proof)
* `docs/proof/m4_2026-01-22_docs_cleanup_gates.txt` — Docs cleanup gates proof (normalizes docs formatting; verifies gates remain green)
* `docs/proof/m4_2026-01-22_prod_compose_deploy_gate.txt` — M4.4 Step 3 (prod-like compose): `python manage.py check --deploy` executed inside container (prod settings)
* `docs/proof/m4_2026-01-22_prod_compose_healthz_smoke.txt` — Prod-like compose host smoke (initial capture; may include redirect behavior depending on curl flags)
* `docs/proof/m4_2026-01-22_prod_compose_healthz_redirect_headers.txt` — Prod-like compose host smoke (redirect/header capture for healthz)
* `docs/proof/m4_2026-01-22_prod_compose_healthz_ipv4_smoke.txt` — Prod-like compose host smoke (IPv4; Windows-safe; confirms `Server: gunicorn`)
* `docs/proof/m4_2026-01-22_gunicorn_server_header_proof.txt` — Gunicorn header proof captured from inside the container (`Server: gunicorn`)
* `docs/proof/m4_2026-01-22_prod_compose_ipv4_docs_index_gates.txt` — Gates proof after indexing prod-compose IPv4 host smoke into docs (index completeness verification)
* `docs/proof/m4_2026-01-22_prod_compose_full_gates.txt` — M4.4 Step 3 (prod-like compose): full gates run inside container (includes `check --deploy`; PASS confirmed)
* `docs/proof/m4_2026-01-22_prod_compose_pid1_cmdline.txt` — M4.4 Step 3: PID1 commandline proof (`/proc/1/cmdline` confirms Gunicorn as container process)

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

### Milestone 3 — Hardening (complete)

* Buyer due-diligence entry point centralized: `docs/CONTRACTS_AND_PROOFS.md`.
* KPI meaning contract aligned and enforced via tests and proof artifacts.
* Export schema contract is machine-checkable and test-enforced.
* Concurrency and oversell prevention proofs captured (see M3 proof pack).
* Consolidated M3 gates proof captured: `docs/proof/m3_2026-01-21_full_gates_clean.txt`.

## In progress

### Milestone 4 — Deployment baseline (in progress)

* **M4.1 (complete):** Postgres parity via Docker Compose + `purelaka.settings_postgres` proven with gates.
  * Proof: `docs/proof/m4_2026-01-21_postgres_parity_gates.txt`
* **M4.2 (complete):** Dockerfile baseline added; repo gates remain green.
  * Proof: `docs/proof/m4_2026-01-22_dockerfile_gate.txt`
* **M4.3 (complete):** Docker Compose web+db baseline; gates executed inside the app container and confirmed Postgres connectivity (`host=db`, `name=purelaka`).
  * Proof: `docs/proof/m4_2026-01-22_compose_web_db_parity_gates.txt`
* **M4.4 (in progress):** Production-shaped container runtime.
  * **Step 1 (complete):** `/monitoring/healthz/` readiness endpoint + gunicorn dependency.
    * Proof: `docs/proof/m4_2026-01-22_healthz_gunicorn_gates.txt`
  * **Step 2 (complete):** container serves via Gunicorn; parity gates executed inside container under Gunicorn runtime.
    * Proofs: `docs/proof/m4_2026-01-22_gunicorn_runtime_smoke.txt`, `docs/proof/m4_2026-01-22_gunicorn_compose_web_db_parity_gates.txt`
  * **Step 3 (complete):** prod-like compose baseline (host smoke + deploy gate + PID1 + full gates).
    * Proofs:
      * `docs/proof/m4_2026-01-22_prod_compose_deploy_gate.txt`
      * `docs/proof/m4_2026-01-22_prod_compose_healthz_ipv4_smoke.txt`
      * `docs/proof/m4_2026-01-22_prod_compose_healthz_redirect_headers.txt`
      * `docs/proof/m4_2026-01-22_prod_compose_healthz_smoke.txt`
      * `docs/proof/m4_2026-01-22_gunicorn_server_header_proof.txt`
      * `docs/proof/m4_2026-01-22_prod_compose_pid1_cmdline.txt`
      * `docs/proof/m4_2026-01-22_prod_compose_full_gates.txt`
      * `docs/proof/m4_2026-01-22_prod_compose_ipv4_docs_index_gates.txt`

* Docs/proof indexing verified after updates:
  * `docs/proof/m4_2026-01-22_docs_index_gates.txt`
  * `docs/proof/m4_2026-01-22_post_index_full_gates.txt` (authoritative post-index full gates snapshot)

## Top blockers (max 3)

1. **Finish M4.4 Step 3 as “closed”:** ensure the latest Step 3 proof pack is complete and consistently indexed (STATUS + CONTRACTS_AND_PROOFS).
2. **Prod-like operational clarity:** document exactly how to run prod-compose locally (commands + expected outputs) in the runbook to reduce buyer friction.
3. **Hardening follow-through:** confirm no environment drift between dev/parity/prod-like modes (explicitly documented rules for `DJANGO_SETTINGS_MODULE` usage).

## Next 3 actions (strict, step-by-step)

1. **Index completeness check:** confirm every Step 3 proof file listed above is present in both `docs/STATUS.md` and `docs/CONTRACTS_AND_PROOFS.md`.
2. **Repeatable Step 3 re-run (optional but strong):** re-run the prod-compose “full gates” once from a clean rebuild and confirm PASS is captured in `docs/proof/m4_2026-01-22_prod_compose_full_gates.txt` (or a new timestamped proof if you prefer).
3. **Mark Step 3 complete when consistent:** once indexing is complete and proof is PASS, flip “Current step” to the next planned item (or explicitly mark M4.4 Step 3 complete and define the next milestone step).
