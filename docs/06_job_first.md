# docs/06_job_first.md (v3.1) — Job-First Checklist (Recruiter / Hiring-Manager Ready)

This checklist is marked **Done/Not Done** based only on evidence found in the uploaded project ZIP (no assumptions).
Where something is partially present or contradicted, it remains **Not Done**.

---

## J0) “Do not embarrass the reviewer” blockers (highest priority)

### J0.1 Deliverable hygiene + clean reviewer bundle
- [x] Deliverable hygiene (ZIP-safe): reviewer bundle generated from git only and repo does not track local artifacts (`.env`, `db.sqlite3`, `.venv/`, IDE/caches) (**Done** — reviewer ZIP via `git archive` proven; local archive ZIP untracked + ignored; see `docs/proof/job_2026-01-24_j0_1_clean_share_zip.txt` and `.gitignore`)
- [x] Generate the reviewer ZIP from git only (recommended standard): `git archive -o purelaka_clean_share.zip HEAD` (**Done** — proof: `docs/proof/job_2026-01-24_j0_1_clean_share_zip.txt`)

### J0.2 Correctness landmines (must eliminate)
- [x] Fix StripeEvent correctness (no properties referencing missing fields) (**Done** — `payments/models.py` contains no reference to `mrr_pennies`)
- [x] Add regression test preventing missing-field properties from returning (StripeEvent “missing field” foot-gun cannot reappear) (**Done** — `payments/tests/test_stripeevent_regression.py` asserts StripeEvent does not expose `mrr_gbp` and explicitly guards against `mrr_pennies`-style regressions)

### J0.3 Canonical status spelling (data integrity)
- [x] Normalize status spelling to canonical `canceled` everywhere (services/tests/templates/docs)  
  Proof: `docs/proof/job_2026-01-24_orders_canceled_normalization_gates.txt`  
  Commit: `1490dd72c905b304e3dcbb0f5798e18d888b5540`

- [x] Add a guard/test preventing invalid status strings from being stored (so `cancelled` cannot silently persist) (**Done** — DB-level constraint `subscription_status_valid` in `subscriptions/models.py` plus regression test `subscriptions/tests/test_subscription_status_guard.py` rejecting `status="cancelled"`)

### J0.4 Claims consistency (proof must match claims)
- [x] Claims consistency: `docs/STATUS.md` must not contradict `docs/acceptance_matrix.md` (**Done** — `docs/STATUS.md` aligns with `docs/acceptance_matrix.md` “Out of scope” section; proof artifact present: `docs/proof/job_2026-01-24_claims_alignment_status_vs_acceptance.txt`)
- [x] Acceptance matrix exists (`docs/acceptance_matrix.md`) (**Done**)

---

## J1) Reliability proof (CI = your “senior signal”)

- [x] CI runs `python manage.py check` (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `python manage.py test` (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `python manage.py run_checks --fail-on-issues` (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `python manage.py makemigrations --check --dry-run` (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `python manage.py check --deploy` (**Done** — `.github/workflows/ci.yml` includes deploy check with `DJANGO_SETTINGS_MODULE: purelaka.settings_prod`)
- [x] CI runs `python manage.py test analyticsapp -v 2` (recommended because analytics is core) (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `ruff check .` (**Done**)
- [x] CI runs `ruff format --check .` (**Done**)
- [x] CI runs `pip-audit` (**Done**)
- [x] Proof artifacts are consistently readable + non-empty (no empty files / bad encoding) (**Done** — proof files normalized to UTF-8 and NUL-byte scan is clean; normalization committed in `105a4d3` for:
  - `docs/proof/job_2026-01-24_job_first_closure_gates_deploy_fix_v5.txt`
  - `docs/proof/job_2026-01-24_job_first_closure_gates_HEAD.txt`
  - `docs/proof/job_2026-01-24_job_first_closure_gates_v5.txt`
  - `docs/proof/job_2026-01-24_job_first_deploy_gate_HEAD.txt`
  - `docs/proof/m1_2026-01-17_audit.txt`
  - `docs/proof/m1_2026-01-17_checks.txt`
  - `docs/proof/m1_2026-01-17_gates.txt`
  - `docs/proof/m3_deploy_gate_2026-01-21.txt`
)

---

## J2) “Reviewer can run it” (minimum docs + reviewer path)

- [x] `README.md` exists (setup context present) (**Done**)
- [x] `.env.example` exists (**Done**)
- [x] README links the acceptance matrix (`docs/acceptance_matrix.md`) so reviewers can verify claims quickly (**Done** — link present in `README.md`)
- [x] `docs/runbook.md` complete and runnable (webhooks, ops, triage, troubleshooting) (**Done** — committed: `716fc7335e078e8858fce59c56805b66f1344ff9`)
- [x] `docs/deployment.md` complete and runnable (prod-like settings, env vars, CSRF/hosts) (**Done** — committed: `2ea6d4f4cd0db42548f2e27f081bd1ac43518c30`)


---

## J3) Senior-level operations controls (what managers care about)

- [x] RBAC documentation exists (`docs/rbac_matrix.md`) (**Done**)
- [x] Audit trail app exists with admin (`audit/models.py`, `audit/admin.py`) (**Done**)
- [ ] Order lifecycle diagram doc exists (`docs/order_state_machine.md`) (**Not Done** — missing)
- [ ] Refund policy doc exists (`docs/refund_policy.md`) (**Not Done** — missing)
- [x] Monitoring “fail then pass” workflow proof captured (create anomaly → issue → resolve) (**Done** — proof: `docs/proof/job_2026-01-24_monitoring_fail_then_pass.txt`)

---

## J4) Analytics credibility (what you demo in interviews)

- [x] KPI definitions exist (`docs/kpi_definitions.md`) (**Done**)
- [x] Snapshot builder exists (`analyticsapp/management/commands/build_analytics_snapshots.py`) (**Done**)
- [x] Dashboard subscription KPI naming matches canonical keys (`canceled`, not `cancelled`) (**Done** — `templates/analytics/dashboard.html` uses `subs.canceled`; verified by `python manage.py test analyticsapp -v 2`)


---

## J5) Demo experience (fast interview demo)

- [ ] Add `docs/demo_walkthrough.md` (5–10 minute demo script by role) (**Not Done** — missing)
- [x] `seed_demo` command exists (`core/management/commands/seed_demo.py`) (**Done**)
- [x] Improve `seed_demo` realism to support the walkthrough (minimum: orders pending/paid/refund-tracked; optional subscriptions only if claimed) (**Done** — `core/management/commands/seed_demo.py` creates pending/paid/fulfilled + refund-tracked order with mock payment refs)


---

## J6) 5-minute demo evidence pack (verification outputs)

These are **outputs** you capture once J0–J5 are green. Store evidence under `docs/proof/demo/` with dated filenames.

- [x] `seed_demo` run output captured (roles created + counts) (**Done** — `docs/proof/demo/demo_2026-01-24_seed_demo_output.txt`)
- [x] Signature proof: `run_checks --fail-on-issues` output showing **0 open issues** (**Done** — `docs/proof/demo/demo_2026-01-24_run_checks_green.txt`)
- [x] Orders export header captured (CSV contract visible) (**Done** — `docs/proof/demo/demo_2026-01-24_export_orders_header.txt`)
- [x] KPI summary export header captured (exec KPI contract visible) (**Done** — `docs/proof/demo/demo_2026-01-24_export_kpi_summary_header.txt`)
- [x] Evidence plan for screenshots exists (**Done** — `docs/proof/demo/README_SCREENSHOTS_PLAN.md`)

### Screenshot evidence (stored under `docs/proof/demo/`)
- [x] Admin login screenshot (**Done** — `docs/proof/demo/demo_2026-01-24_screenshot_login_admin.png`)
- [x] Ops view screenshot (**Done** — `docs/proof/demo/demo_2026-01-24_screenshot_login_ops.png`)
- [x] Analyst dashboard screenshot (**Done** — `docs/proof/demo/demo_2026-01-24_screenshot_login_analyst.png`)
- [x] Executive dashboard screenshot (**Done** — `docs/proof/demo/demo_2026-01-24_screenshot_dashboard_exec.png`)
- [x] Exports page screenshot (**Done** — `docs/proof/demo/demo_2026-01-24_screenshot_exports_page.png`)
- [x] CSV header opened screenshot (**Done** — `docs/proof/demo/demo_2026-01-24_screenshot_csv_header_opened.png`)


## J7) `docs/PROOF_INDEX.md` (reviewer navigation index)

**Requirement:** a reviewer can verify your project in under 2 minutes.  
**Note:** the `docs/PROOF_INDEX.md` file itself should be **links-only** (no checkboxes). This checklist section tracks whether you created it.

- [ ] Create `docs/PROOF_INDEX.md` (**Not Done**)

### PROOF_INDEX.md template (copy/paste; links-only)
> **Product:** Revenue Intelligence for Stripe Commerce  
> **One-line:** Stripe-first revenue analytics + operational controls (reconciled KPIs, governance, exports).  
>
> ## What I built (5–8 bullets)
> - …
>
> ## Where to verify (fast path)
> - README: …
> - Acceptance Matrix: `docs/acceptance_matrix.md`
> - Demo Walkthrough: `docs/demo_walkthrough.md`
>
> ## Proof links
> - CI workflow: `.github/workflows/ci.yml`
> - Latest green CI run (URL): …
> - Status: `docs/STATUS.md`
> - KPI Definitions: `docs/kpi_definitions.md`
> - RBAC Matrix: `docs/rbac_matrix.md`
> - Runbook: `docs/runbook.md`
> - Deployment: `docs/deployment.md`
> - Proof folder: `docs/proof/` (highlight key files)
>
> ## Reproduce locally (copy/paste)
> - `python manage.py check`
> - `python manage.py test`
> - `python manage.py run_checks --fail-on-issues`
> - `python manage.py makemigrations --check --dry-run`
> - `python manage.py check --deploy`

---

## J8) Release hygiene for a professional portfolio project

- [ ] Create missing tags: `v0.2-m2-ops-control`, `v0.3-m3-revenue-intel` (**Not Done** — only `v0.1-m1-audit-clean` present in repo metadata)
