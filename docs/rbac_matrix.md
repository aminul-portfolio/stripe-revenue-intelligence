# RBAC Matrix — Revenue Intelligence for Stripe Commerce

This matrix is the source of truth for role-based access.  
Tests must enforce these rules. UI should hide controls that are not allowed.

## Roles

- **customer**: normal logged-in buyer
- **analyst**: can view analytics + exports + monitoring (read-only operational visibility)
- **ops**: operational role (orders ops + monitoring + analytics/exports)
- **admin**: superuser; full access

## Rules (high level)

- Customer must not access analytics dashboard or exports.
- Analyst/Ops must be allowed to access analytics dashboard and exports.
- Ops/Admin can perform order lifecycle operations (cancel/fulfill).
- Monitoring is restricted to Ops/Analyst/Admin.
- “Hidden 404” is acceptable for protected endpoints where you intentionally conceal existence.

## Endpoint access matrix

Legend: ✅ allowed, ❌ denied (403/404), ↪ redirect to login (302)

| Area | Endpoint / Feature | customer (anon) | customer (logged in) | analyst | ops | admin |
|---|---|---:|---:|---:|---:|---:|
| Auth | Login required pages | ↪ | n/a | n/a | n/a | n/a |
| Analytics | Dashboard (`/analytics/dashboard/?days=7/30/90`) | ↪ | ❌ | ✅ | ✅ | ✅ |
| Analytics | KPI summary export (CSV) | ↪ | ❌ | ✅ | ✅ | ✅ |
| Analytics | Orders export (CSV) | ↪ | ❌ | ✅ | ✅ | ✅ |
| Analytics | Products export (CSV) | ↪ | ❌ | ✅ | ✅ | ✅ |
| Analytics | Customers export (CSV) | ↪ | ❌ | ✅ | ✅ | ✅ |
| Monitoring | Checks UI / pages | ↪ | ❌ | ✅ | ✅ | ✅ |
| Orders | View own order detail | ↪ | ✅ (own only) | ✅ (any, if permitted by policy) | ✅ (any) | ✅ (any) |
| Orders | View other customer’s order | ↪ | ❌ (404) | ✅/❌ (policy-driven; default deny unless explicitly allowed) | ✅ | ✅ |
| Orders Ops | Cancel pending order | ↪ | ❌ | ❌ (unless explicitly allowed) | ✅ | ✅ |
| Orders Ops | Fulfill paid order | ↪ | ❌ | ❌ (unless explicitly allowed) | ✅ | ✅ |
| Payments | Start payment for order | ↪ | ✅ (own order only) | ✅ (policy-driven; default own/ops/admin) | ✅ | ✅ |
| Payments | Webhook endpoint | n/a | n/a | n/a | n/a | n/a |

## Notes / policy decisions

- **Order visibility for analyst**: keep “analyst can view any order” OFF by default unless your product explicitly claims that capability. If enabled, it must be tested and documented.
- **Hide vs 403**: prefer `404` for sensitive endpoints where concealment is part of the security model (common in this repo).

## Tests that should back this

- `accounts.tests.test_rbac_views`
- `analyticsapp.tests.test_access`
- `orders.tests.test_order_access`
- `orders.tests.test_ops_endpoints`
- `analyticsapp.tests.test_exports_csv*` (CSV exports + audit events)

Any change to this matrix requires updating tests and updating `docs/STATUS.md`.
