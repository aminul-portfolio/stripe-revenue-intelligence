# Demo Screenshot Plan (J6) — Revenue Intelligence for Stripe Commerce

This file defines the exact screenshots to capture for the demo evidence pack.
Store the screenshots in this same folder using the filenames below.

## Prerequisites (run first)
- `python manage.py seed_demo`
- `python manage.py run_checks --fail-on-issues`

## Accounts (from seed_demo)
- Admin: `admin / admin12345`
- Ops: `ops / ops12345`
- Analyst: `analyst / analyst12345`
- Customer: use any non-staff user you already have (or create one via admin if needed)

## Required screenshots (1 per item)

### Role logins (one screenshot per role)
1. `demo_2026-01-24_screenshot_login_admin.png`
   - After login: show admin landing page (or admin dashboard) with user visible.

2. `demo_2026-01-24_screenshot_login_ops.png`
   - After login: show Ops-visible page (orders/ops view or analytics access page).

3. `demo_2026-01-24_screenshot_login_analyst.png`
   - After login: show analytics dashboard access as Analyst.

4. `demo_2026-01-24_screenshot_login_customer.png`
   - After login: show customer-visible page (shop/account/orders).

### Executive dashboard (signature screenshot)
5. `demo_2026-01-24_screenshot_dashboard_exec.png`
   - Open analytics dashboard (30d window if selectable).
   - Show KPIs and at least one trend/table element.

### Exports (signature screenshot)
6. `demo_2026-01-24_screenshot_exports_page.png`
   - Open exports page (orders or KPI summary export page is acceptable).

7. `demo_2026-01-24_screenshot_csv_header_opened.png`
   - Open a downloaded CSV in a viewer (Excel/VS Code) and show the header row.
   - Recommended: Orders export or KPI summary export.

## Notes
- These screenshots are intentionally minimal: they prove RBAC surface + dashboards + exports quickly.
- If any page requires staff role, use Ops or Analyst accounts.
