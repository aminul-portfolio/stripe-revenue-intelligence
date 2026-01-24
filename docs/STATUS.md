## Current milestone (job-first)

* Milestone: **Job-First hardening (J0 blockers)**
* Current step: **Close J0 blockers with proof artifacts (hygiene ? correctness ? status normalization ? claims alignment)**
* As-of: **2026-01-24** ? **Job-First baseline gates are PASS and PROVEN anchored** (closure gates + deploy gate + proof index integrity scan)

### Job-First Closure ? 2026-01-24 (PROVEN anchored)

- **PROVEN_COMMIT:** `42ff8ce3caee3f300360ea88f7ce71d84830c440`
- **Proof index:** `docs/CONTRACTS_AND_PROOFS.md` ? section **?Job-First Closure (2026-01-24)?**
- **Authoritative Job-First proofs (PROVEN anchored):**
  - Closure gates: `docs/proof/job_2026-01-24_job_first_closure_gates_HEAD.txt`
  - Deploy gate (prod-like / settings_prod): `docs/proof/job_2026-01-24_job_first_deploy_gate_HEAD.txt`
  - Proof index integrity scan: `docs/proof/job_2026-01-24_contracts_and_proofs_integrity_scan.txt`
- **Note:** ?*_HEAD.txt? filenames are legacy naming; these artifacts are PROVEN anchored via `PROVEN_COMMIT` above.

> Note on Milestone 4: Docker Compose / buyer-ready deployment work exists as historical work-in-repo, but it is **not claimed as shipped** in the Acceptance Matrix ?Out of scope? section until it is re-validated and the Job-First checklist is fully green.

## Runtime baseline

* Python: 3.12.3
* Framework: Django 5.2.10
* DB (dev): SQLite
* Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)
* Postgres parity settings: `DJANGO_SETTINGS_MODULE=purelaka.settings_postgres`
* Container baseline: Dockerfile + Docker Compose (`docker-compose.yml`, `docker-compose.prod.yml`)

## Release gates (latest verified: 2026-01-24)

All gates below must remain green locally and in CI.

* `python manage.py check`: PASS
* `python manage.py test`: PASS (**65 tests**, see latest Job-First proofs)
* `python manage.py run_checks --fail-on-issues`: PASS (**open=0, resolved=3**, see latest proof)
* `python manage.py makemigrations --check --dry-run`: PASS
* `ruff check .`: PASS
* `ruff format --check .`: PASS
* `pip-audit -r requirements.txt`: PASS (see latest proof output)
* Deploy gate (prod-like settings): `python manage.py check --deploy`: PASS (see Job-First deploy proof)
  * Run with: `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`

Latest host proof (default settings, full release gates):
* `docs/proof/m4_2026-01-23_m46_host_full_gates_default.txt`
* `docs/proof/m4_2026-01-23_m46_final_host_full_gates_after_all_docs.txt`
* `docs/proof/m4_2026-01-23_m46_ultimate_host_full_gates.txt`

Final post-push full gates proof (authoritative):
* `docs/proof/m4_2026-01-23_m46_post_push_full_gates.txt`

### Important settings note (prevents false test failures)

* `purelaka.settings_prod` enables deployment protections such as `SECURE_SSL_REDIRECT=True`.
* If you run the test suite with `DJANGO_SETTINGS_MODULE=purelaka.settings_prod`, Django?s test client can receive **301 redirects to `https://testserver/`** for many endpoints.
* Therefore:
  * Run **tests and normal gates** with default settings (`purelaka.settings`), or Postgres parity settings (`purelaka.settings_postgres`).
  * Run **deploy gate only** with prod settings:
    * `DJANGO_SETTINGS_MODULE=purelaka.settings_prod python manage.py check --deploy`
  * After running the deploy gate in PowerShell, clear it:
    * `Remove-Item Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue`

> Note: PowerShell may show a `NativeCommandError` banner when piping/redirection is used (e.g., `Tee-Object`) even if the command succeeds. Treat `$LASTEXITCODE=0` as the authoritative success signal and keep outputs as proof.


## Notes (chronological)

* 2026-01-23: **Ultimate host full gates captured (final host verification):** `docs/proof/m4_2026-01-23_m46_ultimate_host_full_gates.txt`.
* 2026-01-23: **Docs index gates verified after indexing ultimate host proof:** `docs/proof/m4_2026-01-23_m46_docs_index_gates_after_ultimate_host_full_gates.txt`.
* 2026-01-23: **Docs index gates re-verified after indexing the ultimate host verification:** `docs/proof/m4_2026-01-23_m46_docs_index_gates_after_final_host_after_all_docs.txt`.
* 2026-01-23: **Final host full gates re-run after all docs/indexing (ultimate host verification):** `docs/proof/m4_2026-01-23_m46_final_host_full_gates_after_all_docs.txt`.
* 2026-01-23: **Docs index gates captured after indexing the ultimate closure proof:** `docs/proof/m4_2026-01-23_m46_docs_index_gates_after_indexing_ultimate_proof.txt`.
* 2026-01-23: **M4.6 final post-push full gates captured (ultimate closure proof):** `docs/proof/m4_2026-01-23_m46_final_post_push_full_gates.txt`.
* 2026-01-23: **Docs index gates re-verified after indexing the ultimate closure proof:** `docs/proof/m4_2026-01-23_m46_docs_index_gates_after_final_post_push_full_gates.txt`.
* 2026-01-23: **M4 work captured (historical):** final baseline proof + index verification committed (`008d95b`) and stray M3 proof removed (`e3d45cb`). (Not claimed as shipped; see Acceptance Matrix ?Out of scope?.)
* 2026-01-23: **M4.6 final baseline full gates captured (authoritative closure proof):** `docs/proof/m4_2026-01-23_m46_final_baseline_full_gates.txt`.
* 2026-01-23: **M4.6 host full release gates captured (default settings):** `docs/proof/m4_2026-01-23_m46_host_full_gates_default.txt`.
* 2026-01-23: **Docs index gates after host gates (index integrity verification):** `docs/proof/m4_2026-01-23_m46_docs_index_gates_after_host_gates.txt`.
* 2026-01-23: **Post-push full gates captured (authoritative ?after merge? verification):** `docs/proof/m4_2026-01-23_m46_post_push_full_gates.txt`.
* 2026-01-23: **Docs index gates after post-push indexing (index integrity verification):** `docs/proof/m4_2026-01-23_m46_post_push_docs_index_gates.txt`.
* 2026-01-23: **Final after-index full gates captured (?final-final? authoritative proof):** `docs/proof/m4_2026-01-23_m46_final_after_index_full_gates.txt`.
* 2026-01-23: **M4.4 Step 3 prod compose PID1 cmdline captured (Gunicorn is PID1):** `docs/proof/m4_2026-01-22_prod_compose_pid1_cmdline.txt`.
* 2026-01-23: **M4.6 final docs index gates captured (post ?final-final? proof pack verification):** `docs/proof/m4_2026-01-23_m46_final_docs_index_gates_after_final_final.txt`.
* 2026-01-22: **M4.6 STATUS step set; docs/index gates captured (docs-only verification):** `docs/proof/m4_2026-01-22_m46_status_next_step_docs_index_gates.txt`.
* 2026-01-22: **M4.5 marked complete + next-step line added; docs/index gates captured (docs-only verification):** `docs/proof/m4_2026-01-22_m45_complete_status_docs_index_gates.txt`.
* 2026-01-22: **M4.5 docs/index gates after indexing full-gates proofs captured:** `docs/proof/m4_2026-01-22_m45_docs_index_gates_after_updates.txt`.
* 2026-01-22: **M4.5 prod compose full gates captured (in-container):** `docs/proof/m4_2026-01-22_m45_prod_compose_full_gates.txt`.
* 2026-01-22: **M4.5 full gates after updates captured (authoritative baseline):** `docs/proof/m4_2026-01-22_m45_full_gates_after_updates.txt`.
* 2026-01-22: **M4.5 STATUS next-step line added; docs/index gates captured (docs-only verification):** `docs/proof/m4_2026-01-22_m45_status_next_step_docs_index_gates.txt`.
* 2026-01-22: **M4.5 prod compose host healthz (200) captured:** `docs/proof/m4_2026-01-22_m45_prod_compose_host_healthz_headers_200.txt`.
* 2026-01-22: **M4.4 Step 3 rerun docs/index gates captured:** `docs/proof/m4_2026-01-22_prod_compose_rerun_docs_index_gates.txt`.
* 2026-01-22: **M4.4 Step 3 prod compose full gates re-run from clean rebuild (authoritative rerun):** `docs/proof/m4_2026-01-22_prod_compose_full_gates_rerun_clean.txt`.
* 2026-01-22: **M4.4 Step 3 after-fix docs/index gates captured (index completeness):** `docs/proof/m4_2026-01-22_after_fix_docs_index_gates.txt`.
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
* 2026-01-19: Stripe live smoke validated locally (Stripe CLI ? `/payments/webhook/`) with HTTP 200 processing.
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
* 2026-01-20: Acceptance matrix expanded to trace buyer-facing claims ? code ? tests ? proofs (`docs/acceptance_matrix.md` + proof snapshot).
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

### M4 proof pack (closed)

M4.6 closure proofs:

* `docs/proof/m4_2026-01-23_m46_final_baseline_full_gates.txt` ? M4.6 final baseline full gates (authoritative closure proof)
* `docs/proof/m4_2026-01-23_m46_host_full_gates_default.txt` ? M4.6 host full release gates (default settings; fresh capture on 2026-01-23)
* `docs/proof/m4_2026-01-23_m46_index_update_docs_gates.txt` ? M4.6 index update gates (proof indexing verification)
* `docs/proof/m4_2026-01-23_m46_post_close_docs_index_gates.txt` ? M4 post-close docs/index gates (final confirmation)

