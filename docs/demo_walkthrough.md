# Demo Walkthrough (5–10 minutes) — PureLaka

Goal: a recruiter/hiring manager can understand the product value and verify credibility fast.
This walkthrough is designed to be run locally and presented in an interview.

---

## 0) Setup (30–60s)

From repo root:

- `python manage.py check`
- `python manage.py test`

Optional (only if you want seeded demo data):
- `python manage.py seed_demo`

---

## 1) One-minute product framing (say this)

**What it is:** Revenue Intelligence for Stripe Commerce — analytics + operational controls.  
**Why it matters:** It produces decision-grade KPIs and enforces correctness via monitoring, RBAC, and audit trails.  
**Senior signal:** CI runs checks + tests + monitoring gates; proof pack shows “fail then pass” monitoring workflow.

---

## 2) Role-based tour (5–7 minutes total)

> Note: If you don’t have role login credentials pre-created, show the artifacts and admin pages instead.
> This walkthrough is valid as long as you can show the system behavior and proof.

### 2.1 Admin / Ops credibility (2 minutes)

**Show:**
- RBAC matrix doc: `docs/rbac_matrix.md`
- Audit trail admin presence (`audit` app exists, admin registered)

**Say:**
- “RBAC is explicit and documented.”
- “Every operationally meaningful action can be audited.”

**Verify:**
- Open Django admin and show Audit models (if enabled)
- Mention proof pack location: `docs/proof/`

---

### 2.2 Monitoring and reliability gate (2 minutes)

**Show:**
- Run monitoring checks:
  - `python manage.py run_checks --fail-on-issues`
- Proof demonstrating fail→pass:
  - `docs/proof/job_2026-01-24_monitoring_fail_then_pass.txt`

**Say:**
- “This is the operational heartbeat. Any open DataQualityIssue can fail CI.”
- “We can intentionally create an issue, fail the gate, resolve it, and pass again—proven in the proof file.”

---

### 2.3 Analytics value (2–3 minutes)

**Show:**
- KPI definitions: `docs/kpi_definitions.md`
- Snapshot builder exists:
  - `analyticsapp/management/commands/build_analytics_snapshots.py`
- Dashboard uses canonical naming (e.g., `canceled`)

**Say:**
- “KPIs are defined in one source of truth, implemented consistently.”
- “Snapshots provide reproducible reporting windows.”

Optional:
- If running the app, show the dashboard page and KPI tiles/trends.

---

## 3) Proof-driven close (30–60s)

**Show:**
- Acceptance Matrix: `docs/acceptance_matrix.md`
- Status: `docs/STATUS.md`
- Checklist: `docs/06_job_first.md`

**Say:**
- “Claims are verifiable and backed by proofs.”
- “This repo is designed for reviewer speed and correctness-first delivery.”

---

## 4) If asked “what would you do next?”

- Finish J2 runbook + deployment docs (reviewer-friendly operations).
- Add demo evidence pack (screenshots + seed outputs under `docs/proof/demo/`).
- Add PROOF_INDEX quick navigation doc for 2-minute review.

