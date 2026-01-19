# docs/30k_master_checklist.md — £30k Master Checklist (Defensible Execution Tracker)

**Product:** Revenue Intelligence for Stripe Commerce
**Positioning:** Stripe-first revenue analytics + operational controls platform (decision-grade KPIs, reconciled reporting, governance, exports)
**Implementation principle:** Operations Control (foundation) + Reporting Automation (delivery)
**Target outcome:** A deployable, testable, documented, decision-grade analytics product with low buyer risk.

> **Naming discipline (avoid buyer confusion):** Keep repo name, README title, and this document aligned. If repo slug differs from product name, add a one-line mapping in README (e.g., “Repo: stripe-revenue-intelligence; Product: PureLaka Commerce Platform”).

---

## 0) What this checklist is for (the structure you want to rely on)

**Career proof (senior-level delivery):** Operations Control foundations (correctness, audit, RBAC, monitoring).
**Sellable asset (£20k–£30k):** Revenue Intelligence positioning with Reporting Automation delivery (snapshots, exports, scheduled jobs, CI, runbooks).

---

## 1) Release Rule (Definition of Done)

You may only claim **“buyer-ready / sellable £20k–£30k / v1.0”** when ALL are true:

* [ ] Milestones **1–4** complete
* [ ] All **Global Gates** + **Overlays A–F** are green in CI and reproducible locally (or in Docker)
* [ ] A third party can deploy and run the demo from docs in **< 60 minutes**

---

## 2) Global Gates (must be green after every milestone)

Run from project root with venv active.

### 2.1 Core correctness gates (mandatory)

* [ ] `python manage.py check`
* [ ] `python manage.py test`
* [ ] `python manage.py run_checks --fail-on-issues`
* [ ] *(if analytics is part of the core value)* `python manage.py test analyticsapp -v 2`

### 2.2 Release hygiene gates (mandatory for £20k–£30k)

* [ ] `python manage.py makemigrations --check --dry-run`
* [ ] `python manage.py check --deploy` *(run with production settings mode / prod-like env)*

### 2.3 Engineering gates (recommended; include in CI)

* [ ] `ruff check .`
* [ ] `ruff format --check .`
* [ ] `pip-audit -r requirements.txt`

> **Policy for pip-audit:** any High/Critical finding must be fixed (upgrade dependency) or explicitly documented with a remediation plan/date in `docs/security.md`.

> **PowerShell note (proof capture):** when redirecting output for native commands, PowerShell may show a `NativeCommandError` banner even when the command succeeds. Treat `$LASTEXITCODE` as authoritative, and keep the full output in `docs/proof/`.

### Proof artifacts (every milestone)

* [ ] Screenshot or copied terminal output showing all gates green (date/time visible)
* [ ] CI run link (green) + screenshot
* [ ] Commit hash + tag (recommended): `v0.1-m1-audit-clean`, `v0.2-m2-ops-control`, `v0.3-m3-revenue-intel`, `v1.0-m4-buyer-ready`
* [ ] Update `docs/STATUS.md` (current milestone, gates status, blockers, next actions)

---

# Milestone 1 — Audit-clean & runnable (£10k–£15k credibility)

**Objective:** anyone can run it from scratch; no broken modules; no known defects; deterministic tests; CI present.
**Buyer risk removed:** “Can I run it? Can I trust the tests? Are there hidden defects?”

## M1.1 Wishlist resolved (non-negotiable)

Choose ONE and enforce it everywhere:

* [ ] A) Restore wishlist fully (app folder, models, urls, views, templates, tests), OR
* [ ] B) Remove wishlist completely (settings/urls/imports/templates/JS)

**Paths to verify**

* [ ] `wishlist/` *(if included)*
* [ ] `*/templates/*` navigation references
* [ ] project `urls.py`
* [ ] `settings.py` `INSTALLED_APPS`

**Acceptance commands**

* [ ] `python manage.py check`
* [ ] `python manage.py test`

**Proof artifacts**

* [ ] Screenshot: `check` pass
* [ ] README note: “Wishlist included” or “Wishlist intentionally removed” (+ rationale)

---

## M1.2 Monitoring check ↔ DataQualityIssue schema matches (checks must not crash)

**Requirement:** no monitoring check may crash when an issue is detected.

**Paths to verify**

* [ ] `monitoring/models.py` (DataQualityIssue fields)
* [ ] `monitoring/checks/*.py` (all checks)
* [ ] `monitoring/services/run_all.py` (runner resilience)

**Acceptance commands**

* [ ] `python manage.py run_checks`
* [ ] Introduce a known-bad condition and run:

  * [ ] `python manage.py run_checks --fail-on-issues` *(must fail and create issue)*
* [ ] Fix the condition and rerun:

  * [ ] `python manage.py run_checks --fail-on-issues` *(must pass, 0 open issues)*

**Proof artifacts**

* [ ] Screenshot: check fails (issue created)
* [ ] Screenshot: check passes (issues cleared)
* [ ] Admin screenshot: issues show open → resolved workflow

---

## M1.3 StripeEvent model correctness (field/property bug fixed)

**Requirement:** StripeEvent has no properties referencing missing fields; idempotency boundary is coherent.

**Paths to verify**

* [ ] `payments/models.py` (StripeEvent)
* [ ] `payments/services/` (router/handlers)
* [ ] `payments/tests/` (idempotency regression)

**Acceptance commands**

* [ ] `python manage.py check`
* [ ] `python manage.py test`

**Proof artifacts**

* [ ] Commit message: “Fix StripeEvent model correctness”
* [ ] Optional verification:

  * [ ] `python manage.py shell -c "from payments.models import StripeEvent; print([f.name for f in StripeEvent._meta.fields])"`

---

## M1.4 Subscription status mismatch in analytics fixed (canonical: canceled; legacy: cancelled)

**Requirement:** one canonical spelling everywhere (recommended `canceled`).
**Legacy allowance:** historical migrations/comments may contain `cancelled`, but active code/tests/docs must use canonical `canceled`.

**Paths to verify**

* [ ] `subscriptions/models.py` (status choices)
* [ ] `analyticsapp/services/*` and queries
* [ ] `analyticsapp/tests/*` (regression)

**Acceptance commands**

* [ ] `python manage.py test analyticsapp -v 2`
* [ ] `python manage.py test`

**Proof artifacts**

* [ ] Screenshot: analytics tests passing
* [ ] Line added to `docs/kpi_definitions.md`: cancellation status canonical spelling

---

## M1.5 Deterministic tests (no Stripe network dependency)

**Requirement:** tests do not require Stripe CLI or network calls.

**Implementation choices (choose one)**

* [ ] Force `PAYMENTS_USE_STRIPE=0` in tests, OR
* [ ] Mock Stripe client calls in tests, OR
* [ ] Provide a test settings module

**Acceptance commands**

* [ ] Run tests with Stripe disabled:

  * [ ] `python manage.py test`

**Proof artifacts**

* [ ] Screenshot: tests pass with Stripe disabled
* [ ] CI log showing same

---

## M1.6 Repo hygiene (professional handover)

**Must remove from repo/zip**

* [ ] `.env`
* [ ] `db.sqlite3`
* [ ] `.venv/` or `venv/`
* [ ] `.idea/`
* [ ] `__pycache__/`, `*.pyc`

**Must add**

* [ ] `.env.example` (no secrets)
* [ ] `.gitignore`
* [ ] `README.md` (short run steps)

**Acceptance commands**

* [ ] `python manage.py check`
* [ ] `python manage.py test`

**Proof artifacts**

* [ ] Repo tree screenshot (no .env/db/venv)
* [ ] `.env.example` snippet screenshot

---

## M1.7 CI pipeline (reliability proof)

**Requirement:** CI runs the same quality gates (including hygiene + engineering gates).

**Paths to verify**

* [ ] `.github/workflows/ci.yml` (or similar)

**CI steps must run**

* [ ] `python manage.py check`
* [ ] `python manage.py test`
* [ ] `python manage.py run_checks --fail-on-issues`
* [ ] `python manage.py makemigrations --check --dry-run`
* [ ] `python manage.py check --deploy`
* [ ] `ruff check .`
* [ ] `ruff format --check .`
* [ ] `pip-audit -r requirements.txt`

**Acceptance**

* [ ] Push to GitHub; CI green on main

**Proof artifacts**

* [ ] Screenshot: GitHub Actions green
* [ ] CI badge in README

---

### M1 Proof outputs to show your manager

* [ ] Green CI run logs
* [ ] Screenshot: `run_checks --fail-on-issues` shows `0 open issues`
* [ ] “Fresh install” steps in README that work

---

# Milestone 2 — Operations Control hardened (£15k–£20k credibility)

**Objective:** platform behaves safely under real operational conditions (rules enforced, audited, triaged).

## M2.1 Order lifecycle (state machine + rules enforced)

**Rules to enforce in services**

* [ ] `pending → paid → fulfilled`
* [ ] `pending → canceled`
* [ ] `paid → refund` (partial/full) handled by explicit policy decision

**Paths to verify**

* [ ] `orders/services/lifecycle.py`
* [ ] `orders/models.py`
* [ ] `orders/tests/*` (transition tests)

**Acceptance commands**

* [ ] `python manage.py test` *(or `python manage.py test orders -v 2` if you keep per-app gates)*

**Proof artifacts**

* [ ] Diagram screenshot in `docs/order_state_machine.md`
* [ ] Test output snippet showing lifecycle tests passing

---

## M2.2 Refund policy + finance correctness

**Policy must be explicit (documented + implemented)**

* [ ] How refund affects order state
* [ ] Whether restock occurs and when
* [ ] What happens on partial → full refund transitions

**Paths to verify**

* [ ] `docs/refund_policy.md`
* [ ] refund handlers in `payments/services/*`
* [ ] reconciliation check in `monitoring/checks/refund_reconciliation.py`

**Acceptance commands**

* [ ] `python manage.py test`
* [ ] `python manage.py run_checks --fail-on-issues`

**Proof artifacts**

* [ ] Refund policy doc screenshot
* [ ] Screenshot: mismatch creates issue, fixing clears issue

---

## M2.3 Stock integrity (trust builder)

* [ ] Oversell prevention tested (concurrency test or transactional simulation)
* [ ] Preorder logic consistent and documented

**Paths to verify**

* [ ] stock decrement logic (where it lives in your codebase)
* [ ] `orders/services/order_creator.py` (locking)
* [ ] tests proving stock safety

**Acceptance commands**

* [ ] `python manage.py test`

**Proof artifacts**

* [ ] Test output snippet for oversell protection
* [ ] README line: stock decrement rules

---

## M2.4 RBAC + security boundaries (proof)

* [ ] Endpoint audit complete: payments, orders access, ops actions, monitoring, exports, subscriptions
* [ ] Templates hide ops controls from customers
* [ ] RBAC tests exist and pass

**Paths to verify**

* [ ] `accounts/decorators.py`
* [ ] views modules across apps
* [ ] templates showing role-based UI

**Acceptance commands**

* [ ] `python manage.py test`

**Proof artifacts**

* [ ] `docs/rbac_matrix.md` (Role → Allowed actions)
* [ ] UI screenshots per role (customer vs ops/admin)

---

## M2.5 Audit trail (operator-grade)

* [ ] Audit events for: fulfill, cancel, refund updates, stock edits, role changes, exports, snapshots
* [ ] Basic admin “Audit viewer” filters (user/action/date)

**Paths to verify**

* [ ] `audit/models.py`, `audit/admin.py`, `audit/services/logger.py`
* [ ] audit calls from relevant services

**Acceptance commands**

* [ ] `python manage.py test`

**Proof artifacts**

* [ ] Admin screenshot: audit log list + filters
* [ ] Optional: export audit CSV

---

### M2 Proof outputs

* [ ] Refund policy tests + stock protection test are in the suite
* [ ] Admin screenshots: issues queue + audit viewer

---

# Milestone 3 — Revenue Intelligence layer (£20k–£30k credibility)

**Objective:** executive-ready KPIs backed by snapshots and reconciled to Stripe and orders.

## M3.1 KPI definitions (single source of truth)

Create `docs/kpi_definitions.md` including:

* [ ] Revenue definition (gross/net; timing)
* [ ] Refund definition (timing)
* [ ] AOV, repeat rate, cohort/retention, best sellers
* [ ] Subscription metrics (MRR, churn) only if you claim them

**Acceptance**

* [ ] Manual check: every KPI shown in dashboard is defined and matches implementation

**Proof artifacts**

* [ ] KPI glossary screenshot
* [ ] LinkedIn/manager proof: KPI contract summary

---

## M3.2 Snapshot system (automation backbone)

* [ ] Snapshots are authoritative for:

  * daily revenue/orders/refunds
  * customer repeat metrics
  * product rollups (units + revenue)
* [ ] Snapshot reconciliation checks exist and are actionable
* [ ] Defined fix workflow: rebuild snapshots

**Paths to verify**

* [ ] snapshot builder command in `analyticsapp/management/commands/*`
* [ ] reconciliation checks in `monitoring/checks/*`

**Acceptance commands**

* [ ] `python manage.py build_analytics_snapshots --days 30` *(or your command)*
* [ ] `python manage.py run_checks --fail-on-issues`

**Proof artifacts**

* [ ] Snapshot build output screenshot
* [ ] Reconciliation report screenshot (Stripe ↔ Orders ↔ Snapshots alignment)

---

## M3.3 Executive dashboard + exports

**Dashboard pages**

* [ ] Executive overview (7/30/90 + trends)
* [ ] Ops view (exceptions, refunds, fulfillment backlog)
* [ ] Product view (best sellers; margin-ready fields if included)

**Exports**

* [ ] Finance pack: orders, refunds, revenue summary, subscriptions (if included)
* [ ] Ops pack: unfulfilled, anomaly issues
* [ ] BI pack: star-schema friendly export (Power BI ready)

**Acceptance**

* [ ] `python manage.py test analyticsapp -v 2` *(if maintained)*
* [ ] Manual export: confirm schema aligns with KPI definitions doc

**Proof artifacts**

* [ ] Dashboard screenshots
* [ ] Export files showing BI-ready datasets (CSV headers)
* [ ] Audit log entry screenshot for exports

---

### M3 Proof outputs

* [ ] KPI glossary + dashboard screenshots
* [ ] BI-ready export samples
* [ ] Reconciliation evidence

---

# Milestone 4 — Buyer-grade packaging (closes deals at £25k–£30k)

**Objective:** someone else can deploy, operate, and trust it quickly.

## M4.1 Deployment

* [ ] Docker Compose (web + db + redis) OR production guide (gunicorn/nginx/systemd)
* [ ] Production settings checklist: ALLOWED_HOSTS, CSRF, secure cookies, static/media
* [ ] Stripe webhook deployment guide: endpoint + secret management

**Acceptance commands (Docker path)**

* [ ] `docker compose up --build -d`
* [ ] `docker compose exec web python manage.py migrate`
* [ ] `docker compose exec web python manage.py seed_demo`
* [ ] `docker compose exec web python manage.py test`
* [ ] `docker compose exec web python manage.py run_checks --fail-on-issues`
* [ ] `docker compose exec web python manage.py check --deploy`

**Proof artifacts**

* [ ] Screenshot: deploy proof (browser + docker logs)
* [ ] “Deploy in 30–60 minutes” proof note

---

## M4.2 Operations runbook

`docs/runbook.md` must include:

* [ ] Stripe CLI workflow
* [ ] refund operations
* [ ] snapshot scheduling + rebuild rules
* [ ] monitoring triage + resolution
* [ ] troubleshooting guide
* [ ] “When pip-audit fails” remediation procedure

**Proof artifacts**

* [ ] Runbook screenshots + a “fresh install” verification note

---

## M4.3 Demo-in-a-box

* [ ] Seed command creates realistic dataset (products, customers, orders, refunds, subscriptions if included)
* [ ] Demo credentials + walkthrough steps

**Proof artifacts**

* [ ] Demo walkthrough doc (`docs/demo_walkthrough.md`) + screenshots/short video

---

## M4.4 Feature acceptance matrix (no-tampering proof)

* [ ] `docs/acceptance_matrix.md` maps every feature claim to:

  * code files
  * tests
  * demo steps

**Proof artifacts**

* [ ] Acceptance matrix screenshot
* [ ] Link it from README

---

# Release Overlays A–F (Mandatory due diligence)

## Overlay A — Claims integrity

* [ ] Acceptance matrix complete and current
* [ ] Out-of-scope list exists
* [ ] README/LinkedIn claims match matrix exactly

## Overlay B — Security baseline

* [ ] `python manage.py check --deploy` passes in production settings mode
* [ ] Webhook signature verification + idempotency tested
* [ ] Sensitive endpoints role-gated
* [ ] Secrets documented; no secrets committed
* [ ] `pip-audit` High/Critical: fixed or documented with remediation plan/date

## Overlay C — Data governance

* [ ] Identify PII and logging rules (avoid PII)
* [ ] Exports RBAC-protected and audited
* [ ] Retention/anonymization stance documented

## Overlay D — Reproducibility

* [ ] Fresh Postgres migration works via Docker
* [ ] Dependencies pinned/locked with policy documented

## Overlay E — Release engineering

* [ ] Version tags + changelog discipline
* [ ] Upgrade policy documented (migrations + export schema changes)
* [ ] Rollback limitations documented

## Overlay F — Backup/restore validation

* [ ] Backup/restore steps documented
* [ ] One restore validation executed (local or Docker)

---

# Proof Package (LinkedIn + Manager)

Capture and store under `docs/proof/`:

* [ ] CI green screenshot (Actions)
* [ ] `run_checks --fail-on-issues` output (0 open issues)
* [ ] `check --deploy` output screenshot
* [ ] Ruff gates output screenshot (check + format)
* [ ] pip-audit output screenshot (or remediation note)
* [ ] Executive dashboard screenshot (7/30/90 KPIs + trends)
* [ ] Finance export sample (CSV header screenshot)
* [ ] Monitoring issue workflow screenshot (open → resolved)
* [ ] Audit log screenshot (filters visible)
* [ ] Docker deployment proof screenshot (app running + commands)
* [ ] KPI definitions doc screenshot
