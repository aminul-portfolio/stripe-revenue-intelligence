# STATUS — Revenue Intelligence for Stripe Commerce

## Current milestone
- Milestone: M1 Audit-clean & runnable
- Current step: M1.3 StripeEvent correctness review

## Runtime baseline
- Python: 3.12.3
- DB (dev): SQLite
- Target DB (buyer-ready): Postgres (Milestone 4 via Docker Compose)

## Gates (latest: 2026-01-17)
- python manage.py check: PASS
- python manage.py test: PASS (37 tests)
- python manage.py run_checks --fail-on-issues: PASS (0 open issues)
- ruff check .: PASS
- ruff format --check .: PASS
- pip-audit: PASS (no known vulnerabilities)


## Notes (2026-01-17)
- Ruff formatting applied: 2 files reformatted; formatting gate now green


## Evidence
- docs/proof/m1_2026-01-17_gates.txt
- docs/proof/m1_2026-01-17_checks.txt
- docs/proof/m1_2026-01-17_audit.txt

## Completed in M1
- M1.1 Wishlist: INCLUDED and wired (INSTALLED_APPS + urls + template moved to wishlist/templates/wishlist)
- M1.2 Monitoring checks: negative-case proven (open issues created + resolved; gate fails/passes as expected)
- M1.5 Deterministic tests: PASS with PAYMENTS_USE_STRIPE=0; tests contain no Stripe SDK calls

## Top blockers (max 3)
1) M1.3 StripeEvent model correctness not yet verified against checklist
2) M1.4 Subscription KPI/status consistency not yet re-verified after changes
3) CI workflow status not yet confirmed in this session (M1.7)

## Next 3 actions
1) M1.3: Verify StripeEvent fields/properties and remove any wrong property references
2) M1.4: Confirm canceled vs cancelled consistency + analytics test proof
3) M1.7: Add/verify GitHub Actions CI gates
