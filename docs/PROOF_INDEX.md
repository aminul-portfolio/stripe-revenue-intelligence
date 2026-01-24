# Proof Index — Revenue Intelligence for Stripe Commerce (PureLaka)

**One-line:** Stripe-first revenue analytics + operational controls (reconciled KPIs, governance, exports).

## What I built (fast summary)
- Revenue analytics dashboard (revenue, orders, AOV, refunds, customers, subscriptions, churn).
- Deterministic analytics snapshots (daily builds) with window completeness signaling.
- Exportable datasets (orders/products/customers/KPI summary CSV) with contract-tested headers.
- Role-based access control (Admin / Ops / Analyst / Customer) enforced across analytics + exports.
- Audit trail for sensitive actions (exports + key operations).
- Monitoring checks with “fail on issues” gating via `run_checks --fail-on-issues`.
- CI reliability gates (ruff, pip-audit, checks, migrations dry-run, tests).

## Where to verify (2-minute path)
- README: `README.md`
- Acceptance Matrix (claims): `docs/acceptance_matrix.md`
- Job-First Checklist (status): `docs/06_job_first.md`
- Current Status: `docs/STATUS.md`

## Proof links (open these)
- CI workflow: `.github/workflows/ci.yml`
- Proof folder: `docs/proof/`
- J0.1 clean reviewer ZIP proof: `docs/proof/job_2026-01-24_j0_1_clean_share_zip.txt`
- Proof normalization commit reference (readable proofs): see latest proof files under `docs/proof/`

## Reproduce locally (copy/paste)
- `python manage.py check`
- `python manage.py test`
- `python manage.py test analyticsapp -v 2`
- `python manage.py run_checks --fail-on-issues`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py check --deploy`
