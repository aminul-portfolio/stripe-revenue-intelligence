# STATUS — Revenue Intelligence for Stripe Commerce

## Current milestone

- Milestone: M1 Audit-clean & runnable
- Current step: M1.10 Proof pack + docs finalized (local gates + CI green + README buyer-ready)

## Runtime baseline

- Python: 3.12.3
- DB (dev): SQLite
- Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)

## Gates (latest: 2026-01-18)

- python manage.py check: PASS
- python manage.py test: PASS (37 tests)
- python manage.py run_checks --fail-on-issues: PASS (open=0, resolved=3)
- ruff check .: PASS
- ruff format --check .: PASS
- pip-audit -r requirements.txt: PASS (no known vulnerabilities)

## Notes

- 2026-01-17: Ruff formatting applied; formatting gate green.
- 2026-01-17: Monitoring negative-case proven (open issues created; gate failed; then resolved; gate passed).
- 2026-01-18: Git initialized, commits created, CI workflow added, and repo pushed to GitHub.
- 2026-01-18: Settings hardened for CI import stability:
  - SECRET_KEY supports both DJANGO_SECRET_KEY and SECRET_KEY (fallback to dev default)
  - Stripe env validation enforced only when PAYMENTS_USE_STRIPE=1 (safe for CI/tests)
- 2026-01-18: Requirements finalized using pip-tools lockfiles:
  - inputs: requirements.in, requirements-dev.in (human-edited)
  - locks: requirements.txt, requirements-dev.txt (generated via pip-compile; transitive deps pinned)
- 2026-01-18: Subscription KPI regression fixed:
  - KPIs use canonical status "canceled"
  - Window logic stabilized with end-boundary grace to avoid microsecond flakiness
  - Accidental KPI code in test module removed; service restored; tests stable locally + CI
- Subscription “cancelled” remains only in historical migrations/comments; active code/tests must use canonical “canceled”.

## Evidence

- docs/proof/m1_2026-01-17_gates.txt
- docs/proof/m1_2026-01-17_checks.txt
- docs/proof/m1_2026-01-17_audit.txt
- docs/proof/m1_2026-01-18_gates.txt
- docs/proof/m1_2026-01-18_tests.txt
- docs/proof/m1_2026-01-18_run_checks.txt
- docs/proof/m1_2026-01-18_ruff_check.txt
- docs/proof/m1_2026-01-18_ruff_format.txt
- docs/proof/m1_2026-01-18_pip_audit.txt
- docs/proof/m1_2026-01-18_ci_green.txt

## Completed in M1

- M1.1 Wishlist: INCLUDED and wired (INSTALLED_APPS + urls + template moved to wishlist/templates/wishlist)
- M1.2 Monitoring checks: negative-case proven (open issues created + resolved; gate fails/passes as expected)
- M1.3 StripeEvent correctness: VERIFIED via targeted tests and idempotency boundary checks (proof captured)
- M1.4 Subscription KPI window logic: FIXED (consistent window + canonical "canceled" + stable churn calculation; tests stable locally + CI)
- M1.5 Deterministic tests: PASS with PAYMENTS_USE_STRIPE=0; tests contain no Stripe SDK calls
- M1.6 Repo hygiene: .gitignore hardened; .env, db.sqlite3, .venv ignored; proof pack stored under docs/proof/
- M1.7 CI pipeline: GitHub Actions workflow added for global gates; workflow installs deterministic dependencies (requirements-dev.txt); CI confirmed green
- M1.8 Requirements strategy: IMPLEMENTED (pip-tools lockfiles for deterministic installs)
- M1.9 README buyer-ready: CI badge + deterministic install guidance + release gates + no default passwords in docs

## Top blockers (max 3)

1. Proof pack completeness: ensure all 2026-01-18 proof files are committed and referenced above
2. Milestone transition: define M2 feature acceptance checklist (buyer-facing) and map each feature to proof + tests
3. M4 planning: draft Docker Compose + Postgres target shape (keep blocked until M2/M3 are stable)

## Next 3 actions

1. Commit the 2026-01-18 proof artifacts and the updated README/STATUS (single “Docs + proof pack” commit)
2. Create M2 feature acceptance checklist (Definition-of-Done per feature, with linked routes/tests/proofs)
3. Start M2 step-by-step (one feature gap or polish item at a time, each ending with green gates + proof)
