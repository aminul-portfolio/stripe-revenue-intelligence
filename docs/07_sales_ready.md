# docs/07_sales_ready.md — Future Sales Checklist (£30k Buyer-Ready)

This checklist is marked **Done/Not Done** based only on evidence found in the uploaded project ZIP (no assumptions).
Where something is partially present or contradicted, it remains **Not Done**.

---

## S0) Buyer “red line” blockers (must be clean)
- [ ] Clean deliverable package (no secrets/DB/venv/IDE caches in distributed ZIP) (**Not Done**)
- [ ] Buyer/reviewer deliverable ZIP generated from git history only: `git archive -o purelaka_clean_share.zip HEAD` (**Not Done**)
  - [ ] Confirm ZIP contains no `.env`, `db.sqlite3`, `.venv/`/`venv/`, IDE folders, caches (**Not Done**)
- [ ] StripeEvent defect fixed + regression test (**Not Done**)
- [ ] canceled/cancelled normalized + regression test (**Not Done**)
- [ ] Claims integrity: README/STATUS/acceptance matrix aligned, no contradictions (**Not Done**)

---

## S1) Buyer-grade CI gates parity (must match your DoD)
- [x] CI: `check`, `test`, `run_checks --fail-on-issues` (**Done**)
- [x] CI: `makemigrations --check --dry-run` (**Done**)
- [x] CI: ruff (check + format) (**Done**)
- [x] CI: pip-audit (**Done**)
- [ ] CI: `check --deploy` enforced (**Not Done**)
- [ ] CI: `test analyticsapp -v 2` enforced (**Not Done**)

---

## S2) Deployment proof (repeatable, third-party friendly)
- [x] Docker/Compose files exist (`docker-compose.yml`, `docker-compose.prod.yml`, `Dockerfile`) (**Done**)
- [ ] Fresh DB reproducibility proof (Docker + Postgres): (**Not Done**)
  - [ ] Start from an empty Postgres volume (new volume) (**Not Done**)
  - [ ] Run migrations from scratch (**Not Done**)
  - [ ] Run `seed_demo` (**Not Done**)
  - [ ] Run gates inside Docker: `test`, `run_checks --fail-on-issues`, `check --deploy` (**Not Done**)
  - [ ] Capture readable proof log + screenshots (browser + docker logs) (**Not Done**)
- [ ] One-command bring-up is documented (exact commands + env + troubleshooting) (**Not Done** — deployment docs incomplete)
- [ ] Full Docker acceptance proof captured (commands + outputs + screenshots) (**Not Done**)

---

## S3) Reporting automation (scheduled snapshots)
- [ ] Scheduling implemented (Celery beat or documented cron) (**Not Done** — no credible scheduling implementation)
- [ ] Scheduling documented in runbook (retry policy, failure visibility, manual rerun) (**Not Done**)

---

## S4) Demo-in-a-box (sales enablement)
- [x] `seed_demo` command exists (`core/management/commands/seed_demo.py`) (**Done**)
- [ ] Demo dataset is realistic: customer + pending/paid/refunded orders (+ subs only if claimed) (**Not Done** — seed is partial)
- [ ] Demo walkthrough exists (`docs/demo_walkthrough.md`, 5–10 minutes) (**Not Done**)
- [ ] Role-based demo proof screenshots (admin/ops/analyst/customer) (**Not Done**)

---

## S5) Acceptance matrix (no-tampering proof pack)
- [x] `docs/acceptance_matrix.md` exists (**Done**)
- [ ] Acceptance matrix is current and consistent with shipped state and STATUS (**Not Done** — contradictions exist)
- [ ] Acceptance matrix is linked from README (**Not Done**)

---

## S6) Due diligence overlays (required for credible £30k)
- [ ] Overlay A — Claims integrity: out-of-scope list maintained; claims match matrix exactly (**Not Done**)
- [ ] Overlay B — Security baseline: `check --deploy` green in CI; secrets handling documented; pip-audit remediation policy in `docs/security.md` (**Not Done** — partial, missing required pieces)
- [ ] Overlay C — Data governance: `docs/data_governance.md` (PII inventory, logging policy, retention) (**Not Done**)
- [ ] Overlay D — Reproducibility: fresh Postgres migrate from empty DB via Docker proven (**Not Done**)
- [ ] Overlay E — Release engineering: `docs/release_process.md` (upgrade/migration & export schema policy) (**Not Done**)
- [ ] Overlay F — Backup/restore: `docs/backup_restore.md` + restore validation proof (**Not Done**)

---

## S7) Proof pack quality (buyers judge evidence, not claims)
- [ ] Replace empty proof files with valid captures (**Not Done**)
- [ ] Re-capture proofs in readable UTF-8 text (avoid null-byte/UTF-16 captures) (**Not Done**)
- [ ] Provide a single “proof index” doc linking all evidence artifacts (**Not Done**)
- [ ] Release tags created (and referenced in proof index): (**Not Done**)
  - [ ] `v0.2-m2-ops-control` (**Not Done**)
  - [ ] `v0.3-m3-revenue-intel` (**Not Done**)
  - [ ] `v1.0-m4-buyer-ready` (**Not Done**)

---

## S8) Extra implementation required for genuinely buyer-ready £30k (beyond current repo)
### Productization and buyer operations
- [ ] Licensing/IP package: license file, third-party attribution, clear transfer statement
- [ ] Configuration hardening: secrets management guide (env vars, key rotation guidance, no secrets in logs)
- [ ] Supportability: known limitations + operational assumptions + handover checklist
- [ ] Upgrade compatibility: explicit migration/upgrade policy and “breaking changes” rules for exports/KPI definitions
- [ ] Multi-environment separation: dev/staging/prod settings model documented and enforced

### Observability beyond checks
- [ ] Structured logging (request IDs; correlation for exports/snapshot runs)
- [ ] Health endpoint / readiness check (`/healthz`)
- [ ] Alerting guidance (snapshot freshness, reconciliation drift, failed jobs)

### Security & compliance baseline (buyer expectation)
- [ ] PII review: exports/logs avoid PII or define masking policy
- [ ] Webhook threat notes: replay prevention, idempotency boundary documented
- [ ] Dependency strategy: pinned versions + patch cadence

### Data durability
- [ ] Backups automated (schedule documented + restore drills)
- [ ] Database migration “zero-to-live” documented and proven in Docker
