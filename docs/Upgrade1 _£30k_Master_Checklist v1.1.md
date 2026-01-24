# Outstanding Work — Job-First (v1.1) — Minimal

## Highest-risk credibility blockers (do these first)
- [ ] Remove deliverable leaks: ensure distributed ZIP contains no `.env`, `.venv/`, `db.sqlite3`, `.idea/`, `.ruff_cache/`
- [ ] Fix StripeEvent correctness: remove/repair `StripeEvent.mrr_pennies` property (add migration or delete property) + add regression test
- [ ] Normalize status spelling: use **canceled** everywhere (code, templates, tests, monitoring comments, migrations) — eliminate `cancelled`
- [ ] Finish runbook: complete `docs/runbook.md` (webhook setup, Stripe CLI, refund ops, snapshot rebuild, monitoring triage, troubleshooting)
- [ ] Finish deployment docs: complete `docs/deployment.md` (env vars, DEBUG off checklist, ALLOWED_HOSTS/CSRF, webhook config, prod settings)
- [ ] Claims alignment: reconcile `docs/STATUS.md` vs `docs/acceptance_matrix.md` (no “M4 complete” if matrix says out-of-scope)

## Global gates / CI parity
- [ ] Add `python manage.py check --deploy` to CI workflow
- [ ] Decide on analytics test gate and enforce in CI (`python manage.py test analyticsapp -v 2`) or remove from required gates
- [ ] Ensure proof artifacts are readable text (avoid UTF-16/BOM captures)

## Milestone 2 hardening gaps
- [ ] Add/complete `docs/refund_policy.md` and ensure reconciliation check exists + proof (issue created then resolved)
- [ ] Add at least one explicit audit-log test (or acceptance-matrix proof) for critical ops actions + exports

## Milestone 4 buyer packaging gaps
- [ ] Implement scheduling for daily snapshots (Celery beat or documented cron) + proof logs
- [ ] Add `docs/demo_walkthrough.md` (5–10 minute demo script)
- [ ] Improve `seed_demo` to create: admin/ops/analyst/customer + realistic orders (pending/paid/refunded) + optional subscription rows
- [ ] Ensure Docker Compose docs are “one command bring-up” and match repo files + proofs

## Release DoD overlays (A–F) — required for “£30k-ready”
- [ ] Overlay A: maintain out-of-scope list + ensure README/LinkedIn claims map to acceptance matrix rows
- [ ] Overlay B: expand `docs/security.md` (webhook signature, idempotency tests, secrets handling) + CI `check --deploy`
- [ ] Overlay C: add `docs/data_governance.md` (PII inventory, logging policy, export access, retention/anonymization stance)
- [ ] Overlay D: document reproducibility policy (pinning strategy, fresh Postgres migrations via Docker)
- [ ] Overlay E: add `docs/release_process.md` (tags, upgrade/migration policy, rollback limits)
- [ ] Overlay F: add `docs/backup_restore.md` + perform one restore validation (log/proof)
