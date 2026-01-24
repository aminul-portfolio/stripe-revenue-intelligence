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
- [ ] Normalize status spelling to canonical `canceled` everywhere (services/tests/templates/docs) (**Not Done** — dashboard template uses `subs.cancelled` and label “Subs (Cancelled)” in `templates/analytics/dashboard.html`)
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
- [ ] Proof artifacts are consistently readable + non-empty (no empty files / bad encoding) (**Not Done** — multiple proof files contain NUL bytes / encoding issues, e.g.:
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
- [ ] `docs/runbook.md` complete and runnable (webhooks, ops, triage, troubleshooting) (**Not Done** — file exists but is not yet end-to-end complete/runnable as an ops runbook)
- [ ] `docs/deployment.md` complete and runnable (prod-like settings, env vars, CSRF/hosts) (**Not Done** — file exists and covers many areas, but completeness/runnability is not fully evidenced; static files/release checklist details are not covered)

---

## J3) Senior-level operations controls (what managers care about)

- [x] RBAC documentation exists (`docs/rbac_matrix.md`) (**Done**)
- [x] Audit trail app exists with admin (`audit/models.py`, `audit/admin.py`) (**Done**)
- [ ] Order lifecycle diagram doc exists (`docs/order_state_machine.md`) (**Not Done** — missing)
- [ ] Refund policy doc exists (`docs/refund_policy.md`) (**Not Done** — missing)
- [ ] Monitoring “fail then pass” workflow proof captured (create anomaly → issue → resolve) (**Not Done** — not proven end-to-end in proofs)

---

## J4) Analytics credibility (what you demo in interviews)

- [x] KPI definitions exist (`docs/kpi_definitions.md`) (**Done**)
- [x] Snapshot builder exists (`analyticsapp/management/commands/build_analytics_snapshots.py`) (**Done**)
- [x] Dashboard subscription KPI naming matches canonical keys (`canceled`, not `cancelled`) (**Done** — `templates/analytics/dashboard.html` uses `subs.canceled`; verified by `python manage.py test analyticsapp -v 2`)


---

## J5) Demo experience (fast interview demo)

- [ ] Add `docs/demo_walkthrough.md` (5–10 minute demo script by role) (**Not Done** — missing)
- [x] `seed_demo` command exists (`core/management/commands/seed_demo.py`) (**Done**)
- [ ] Improve `seed_demo` realism to support the walkthrough (minimum: orders pending/paid/refunded; optional subscriptions only if claimed) (**Not Done** — not evidenced)

---

## J6) 5-minute demo evidence pack (verification outputs)

These are **outputs** you capture once J0–J5 are green. Store evidence under `docs/proof/demo/` with dated filenames.

- [ ] `seed_demo` run output captured (roles created + counts) (**Not Done**)
- [ ] 1 screenshot per role login: Admin / Ops / Analyst / Customer (**Not Done**)
- [ ] Signature screenshot: Executive dashboard (KPIs + trends) (**Not Done**)
- [ ] Signature proof: `run_checks --fail-on-issues` output showing **0 open issues** (**Not Done**)
- [ ] Signature screenshot: Exports page + one CSV header opened (finance pack / BI pack) (**Not Done**)
- [ ] Evidence stored in `docs/proof/demo/` (dated filenames) (**Not Done**)

---

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
