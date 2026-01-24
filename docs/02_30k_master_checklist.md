# 02_30k_master_checklist.md — Outstanding Work (Minimal)

This file tracks only the items that are **Not Met** or **Partially Met** against `docs/30k_master_checklist.md`.

---

## A) Release Rule blockers
- [ ] Milestones 1–4 complete (see sections C–F)
- [ ] Global Gates + Overlays A–F all green in CI and reproducible locally (or in Docker)
- [ ] Third-party can deploy and run demo from docs in < 60 minutes

---

## B) Global Gates (outstanding)
- [ ] Add CI gate: `python manage.py check --deploy` (production settings mode)
- [ ] Add CI gate (if analytics is core value): `python manage.py test analyticsapp -v 2`
- [ ] Re-capture/replace any empty proof artifacts (e.g., empty pip-audit proof file)
- [ ] Re-capture/replace any non-readable proof outputs (UTF-16 / null-byte captures)
- [ ] Create missing tags: `v0.2-m2-ops-control`, `v0.3-m3-revenue-intel`, `v1.0-m4-buyer-ready`

---

## C) Milestone 1 — Audit-clean & runnable (outstanding)
- [ ] M1.2 Prove monitoring “fail then pass” workflow:
  - [ ] create anomaly → `run_checks --fail-on-issues` fails + creates issue
  - [ ] fix anomaly → `run_checks --fail-on-issues` passes (0 open issues)
  - [ ] admin screenshot: open → resolved
- [ ] M1.3 Fix StripeEvent correctness defect (`payments/models.py` missing-field property)
- [ ] M1.4 Normalize canceled vs cancelled end-to-end (services, templates, tests, docs)
- [ ] M1.6 Deliverable hygiene: remove from any shared ZIP: `.env`, `db.sqlite3`, `.venv/venv`, `.idea/`, caches, `__pycache__/`
- [ ] M1.7 CI parity: ensure CI runs the full gate set required by checklist (includes `check --deploy` and analyticsapp tests if kept)

---

## D) Milestone 2 — Operations Control hardened (outstanding)
- [ ] M2.1 Add `docs/order_state_machine.md` (diagram + rules) and ensure lifecycle uses valid canonical statuses only
- [ ] M2.2 Create `docs/refund_policy.md` and align implementation + reconciliation check proof (mismatch → issue; fixed → cleared)

---

## E) Milestone 3 — Revenue Intelligence layer (outstanding)
- [ ] Fix dashboard subscription KPI naming to match canonical status keys (ties to canceled vs cancelled fix)

---

## F) Milestone 4 — Buyer-grade packaging (outstanding)
- [ ] M4.1 Produce a complete deploy proof (Docker path):
  - [ ] `docker compose up --build -d`
  - [ ] migrate + seed_demo
  - [ ] `test`, `run_checks --fail-on-issues`, `check --deploy`
  - [ ] browser + docker logs screenshots
- [ ] M4.2 Complete `docs/runbook.md` (Stripe CLI, refunds, scheduling, triage, troubleshooting, pip-audit remediation)
- [ ] M4.3 Complete `seed_demo` realism (customer + orders pending/paid/refunded + optional subs) and add `docs/demo_walkthrough.md`
- [ ] M4.4 Link `docs/acceptance_matrix.md` from README and keep it current

---

## G) Release Overlays A–F (mandatory due diligence) — outstanding
- [ ] Overlay A: resolve `docs/STATUS.md` vs `docs/acceptance_matrix.md` contradictions; claims match matrix exactly
- [ ] Overlay B: update `docs/security.md` (pip-audit remediation policy, secrets handling, deploy-check proof refs)
- [ ] Overlay C: add `docs/data_governance.md` (PII, logging rules, export access, retention stance)
- [ ] Overlay D: document reproducibility policy + prove fresh Postgres migration via Docker from empty DB
- [ ] Overlay E: add `docs/release_process.md` (tags, upgrade/migrations, export schema change policy, rollback limits)
- [ ] Overlay F: add `docs/backup_restore.md` + perform one restore validation with proof logs

---

## H) Proof Package gaps (recapture as needed)
- [ ] Current CI green screenshot/link
- [ ] `run_checks --fail-on-issues` output showing 0 open issues
- [ ] `check --deploy` output (after CI gate added)
- [ ] pip-audit output (non-empty) + remediation note if needed
- [ ] Executive dashboard screenshot (7/30/90 + trends)
- [ ] Finance export CSV header screenshot
- [ ] Monitoring workflow screenshot (open → resolved)
- [ ] Audit log screenshot (filters visible)
- [ ] Docker deployment proof (running app + commands)
- [ ] KPI definitions doc screenshot
