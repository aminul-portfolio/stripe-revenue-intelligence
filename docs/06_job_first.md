# docs/06_job_first.md (v3.1) — Job-First Checklist (Recruiter / Hiring-Manager Ready)

This checklist is marked **Done/Not Done** based only on evidence found in the uploaded project ZIP (no assumptions).
Where something is partially present or contradicted, it remains **Not Done**.

---

## J0) “Do not embarrass the reviewer” blockers (highest priority)

### J0.1 Deliverable hygiene + clean reviewer bundle
- [ ] Deliverable hygiene (ZIP-safe): remove from any shared ZIP/package: `.env`, `db.sqlite3`, `.venv/venv`, `.idea/`, `.ruff_cache/`, `__pycache__/`, `*.pyc`, `.pytest_cache/` (**Not Done** — present in uploaded ZIP)
- [ ] Generate the reviewer ZIP from git only (recommended standard): `git archive -o purelaka_clean_share.zip HEAD` (**Not Done** — cannot be proven from ZIP)

### J0.2 Correctness landmines (must eliminate)
- [ ] Fix StripeEvent correctness (no properties referencing missing fields) (**Not Done** — `payments/models.py` references missing `mrr_pennies`)
- [ ] Add regression test preventing missing-field properties from returning (StripeEvent “missing field” foot-gun cannot reappear) (**Not Done** — no dedicated regression guard evidenced)

### J0.3 Canonical status spelling (data integrity)
- [ ] Normalize status spelling to canonical `canceled` everywhere (services/tests/templates/docs) (**Not Done** — mismatches; dashboard expects `subs.cancelled`)
- [ ] Add a guard/test preventing invalid status strings from being stored (so `cancelled` cannot silently persist) (**Not Done** — not evidenced)

### J0.4 Claims consistency (proof must match claims)
- [ ] Claims consistency: `docs/STATUS.md` must not contradict `docs/acceptance_matrix.md` (**Not Done** — contradiction present)
- [x] Acceptance matrix exists (`docs/acceptance_matrix.md`) (**Done**)

---

## J1) Reliability proof (CI = your “senior signal”)

- [x] CI runs `python manage.py check` (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `python manage.py test` (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `python manage.py run_checks --fail-on-issues` (**Done** — `.github/workflows/ci.yml`)
- [x] CI runs `python manage.py makemigrations --check --dry-run` (**Done** — `.github/workflows/ci.yml`)
- [ ] CI runs `python manage.py check --deploy` (**Not Done** — not in CI)
- [ ] CI runs `python manage.py test analyticsapp -v 2` (recommended because analytics is core) (**Not Done** — not in CI)
- [x] CI runs `ruff check .` (**Done**)
- [x] CI runs `ruff format --check .` (**Done**)
- [x] CI runs `pip-audit` (**Done**)
- [ ] Proof artifacts are consistently readable + non-empty (no empty files / bad encoding) (**Not Done** — empty and UTF-16-like proofs exist)

---

## J2) “Reviewer can run it” (minimum docs + reviewer path)

- [x] `README.md` exists (setup context present) (**Done**)
- [x] `.env.example` exists (**Done**)
- [ ] README links the acceptance matrix (`docs/acceptance_matrix.md`) so reviewers can verify claims quickly (**Not Done** — link not present)
- [ ] `docs/runbook.md` complete and runnable (webhooks, ops, triage, troubleshooting) (**Not Done** — incomplete)
- [ ] `docs/deployment.md` complete and runnable (prod-like settings, env vars, CSRF/hosts) (**Not Done** — incomplete)

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
- [ ] Dashboard subscription KPI naming matches canonical keys (`canceled`, not `cancelled`) (**Not Done** — template mismatch)

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
