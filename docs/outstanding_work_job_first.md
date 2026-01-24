# docs/outstanding_work_job_first.md — Outstanding Work (Job-First)

This is a minimal tracker of all items that are **not yet complete** (Not Met or Partially Met), based strictly on current repo evidence.

---

## A) Critical credibility blockers (do first)

### A1) Deliverable hygiene (repo/package cleanliness)
- [ ] Ensure `.env` is not tracked and not shipped
- [ ] Ensure `db.sqlite3` is not tracked and not shipped
- [ ] Ensure `venv/` and/or `.venv/` are not tracked and not shipped
- [ ] Ensure `.idea/` is not tracked and not shipped
- [ ] Ensure `.ruff_cache/` is not tracked and not shipped
- [ ] Ensure `__pycache__/` is not tracked and not shipped
- [ ] Confirm `.gitignore` blocks all the above
- [ ] Produce a clean reviewer ZIP from git (recommended): `git archive -o purelaka_clean_share.zip HEAD`

### A2) StripeEvent correctness defect
- [ ] Fix `payments/models.py`: remove or correct `StripeEvent.mrr_gbp` referencing missing `mrr_pennies`
- [ ] Add a regression test to prevent this defect returning (recommended)
- [ ] Run and capture gates after fix: `check`, `test`, `run_checks --fail-on-issues`

### A3) “canceled vs cancelled” consistency
- [ ] Standardise spelling across code: `orders/services/lifecycle.py`
- [ ] Standardise spelling across tests: `orders/tests/**`
- [ ] Standardise spelling across templates (if any)
- [ ] Confirm zero repo occurrences of the wrong spelling (search/grep)
- [ ] Add a test/guard preventing invalid status strings

### A4) Operator docs completeness (runbook + deployment)
- [ ] Fully complete `docs/runbook.md` (no truncation; runnable steps)
- [ ] Fully complete `docs/deployment.md` (no truncation; real checklist)
- [ ] Ensure docs match actual commands/files in repo

### A5) Claims alignment (STATUS vs acceptance matrix)
- [ ] Align `docs/STATUS.md` with `docs/acceptance_matrix.md` (no contradictions)
- [ ] Ensure no item is “out-of-scope/not shipped” while also claimed as complete

---

## B) Global gates enforcement (if you keep analytics as a formal gate)

### B1) Enforce analytics tests in CI
- [ ] Decide to keep `python manage.py test analyticsapp -v 2` as a formal gate
- [ ] If kept: add it to `.github/workflows/ci.yml` and verify CI green

---

## C) Milestone 2 outstanding items

### C1) Order lifecycle correctness (state machine)
- [ ] Fix cancel spelling drift in lifecycle so it writes only valid model status values
- [ ] Re-run lifecycle and RBAC tests to confirm no regressions

### C2) Refund policy documentation
- [ ] Create `docs/refund_policy.md` (1 page) and align with code behavior
- [ ] Verify monitoring check behavior matches policy (mismatch → issue → resolved)

---

## D) Milestone 4 outstanding items (sale readiness later; still track now)

### D1) Docker Compose “buyer-grade proof”
- [ ] Ensure Docker run steps are documented and reproducible
- [ ] Provide proof commands + outputs for docker bring-up, migrate, seed, test, run_checks

### D2) Scheduling (reporting automation)
- [ ] Implement daily snapshot scheduling (Celery beat or cron; choose one)
- [ ] Document schedule, failure handling, and manual trigger

### D3) Demo-in-a-box + walkthrough
- [ ] Create `docs/demo_walkthrough.md` (5–10 minute script)
- [ ] Expand `seed_demo` to include realistic demo data (orders/refunds; subscriptions if claimed)
- [ ] Validate role boundaries in demo accounts (admin/ops/analyst/customer)

### D4) Acceptance matrix defensibility
- [ ] Ensure acceptance matrix matches what is actually shipped
- [ ] Ensure every public claim maps to code paths + tests + demo steps
