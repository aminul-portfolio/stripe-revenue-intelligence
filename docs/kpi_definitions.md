# KPI Definitions — Revenue Intelligence for Stripe Commerce

This document is the single source of truth for KPI meaning and calculation rules.
Every KPI shown in the dashboard or exports must be defined here and must match implementation.

## Scope and time windows

* Supported windows: **7 / 30 / 90 days**
* KPI values are computed for the selected window.
* Source of truth: **analytics snapshots** for revenue/orders/refunds/funnel/customer metrics where available.

### Time boundaries

* A window is defined as **“last N days”** relative to `timezone.localdate()` in the application timezone.
* Unless stated otherwise, **“within the window”** means days **inclusive of today** (N calendar days).
* Snapshot-driven KPIs use snapshot days; completeness is surfaced via snapshot metadata (e.g., missing days). If completeness is false, KPI values may be understated.

## Data sources (authoritative order)

1. **Analytics snapshots** (daily snapshot rows + derived rollups)
2. **Orders DB** (raw orders within window; used by some exports and reconciliation)
3. **Stripe** (used for live payments/webhooks; reconciliation checks ensure drift is visible)

## Definitions and measurement policy

### Currency and rounding

* Currency values are presented in store currency (e.g., GBP).
* If the underlying implementation stores pennies/cents, conversions must be consistent across dashboard and exports.
* Rounding rules must be consistent in UI/export formatting (presentation concern), while stored values remain precise (data concern).

### Revenue basis (critical)

* **Revenue** is defined as **gross paid order total** for orders included in snapshots.
* Revenue follows the system-of-record used in snapshots (typically `Order.total` for paid/fulfilled orders).
* If later the platform introduces explicit tax/shipping/discount breakdowns, this section must be updated to specify whether Revenue is gross (includes shipping/tax) or net (excludes them). Until then, Revenue is **the same total that the order system treats as the paid total.**

## KPI glossary

### Export meta fields (KPI summary)

#### 0) Window Days

* **Name:** Window Days
* **Type:** Integer (days)
* **Definition:** The selected KPI window size (allowed values: 7, 30, 90).
* **Source:** Request parameter (echoed in export).
* **Shown in:** KPI export
* **Export column:** `window_days`

#### 0.1) Latest Snapshot Day

* **Name:** Latest Snapshot Day
* **Type:** Date
* **Definition:** The most recent snapshot day used to compute KPI values for the selected window.
* **Source:** Snapshots
* **Notes:** If snapshots are incomplete or lagging, KPI values may be understated and this date helps detect that.
* **Shown in:** KPI export
* **Export column:** `latest_snapshot_day`

### Revenue KPIs

#### 1) Revenue

* **Name:** Revenue
* **Type:** Currency
* **Definition:** Total gross paid order total within the window.
* **Source:** Snapshots
* **Notes:** Revenue is based on paid/fulfilled orders included in snapshots. If snapshot completeness is false, revenue may be understated.
* **Shown in:** Dashboard (overview), KPI export

#### 2) Orders

* **Name:** Orders
* **Type:** Count
* **Definition:** Number of paid orders within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

#### 3) AOV (Average Order Value)

* **Name:** AOV
* **Type:** Currency
* **Definition:** `Revenue / Orders` for the window (**0 if Orders=0**).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

### Refund KPIs

#### 4) Refunded Amount

* **Name:** Refunded Amount
* **Type:** Currency
* **Definition:** Total refunded value within the window.
* **Source:** Snapshots
* **Notes:** Refunded Amount is based on refund fields recorded on orders and aggregated by the snapshot system.
* **Shown in:** Dashboard, KPI export
* **Export column:** `refunded_amount`

#### 5) Refunded Orders

* **Name:** Refunded Orders
* **Type:** Count
* **Definition:** Count of orders that have **any recorded refund** within the window (partial or full).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export
* **Export column:** `refunded_orders`

#### 6) Refund Rate (Orders %)

* **Name:** Refund Rate (Orders %)
* **Type:** Percentage
* **Definition:** `(Refunded Orders / Orders) * 100` (**0 if Orders=0**).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export
* **Export column:** `refund_rate_orders_pct`

#### 7) Refund Rate (Value %)

* **Name:** Refund Rate (Value %)
* **Type:** Percentage
* **Definition:** `(Refunded Amount / Revenue) * 100` (**0 if Revenue=0**).
* **Source:** Derived from snapshot KPIs (Revenue + Refunded Amount).
* **Shown in:** Dashboard (only if displayed)
* **Notes:** This KPI is not part of the current export contract unless explicitly added to `docs/contracts/kpi_contract.json`.

### Customer KPIs

#### 8) Unique Customers

* **Name:** Unique Customers
* **Type:** Count
* **Definition:** Number of distinct purchasing customers within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export
* **Export column:** `unique_customers`

#### 9) Repeat Customers

* **Name:** Repeat Customers
* **Type:** Count
* **Definition:** Number of customers with **2+ purchases** (per snapshot logic) within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export
* **Export column:** `repeat_customers`

#### 10) Repeat Rate (%)

* **Name:** Repeat Rate (%)
* **Type:** Percentage
* **Definition:** `(Repeat Customers / Unique Customers) * 100` (**0 if Unique Customers=0**).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export
* **Export column:** `repeat_rate_pct`

### Funnel KPIs

#### 11) Wishlisted Users

* **Name:** Wishlisted Users
* **Type:** Count
* **Definition:** Number of distinct users who have at least one wishlist action/state within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard funnel, KPI export
* **Export column:** `wishlisted_users`

#### 12) Purchased Users

* **Name:** Purchased Users
* **Type:** Count
* **Definition:** Number of distinct users who purchased within the window (as used by funnel logic).
* **Source:** Snapshots
* **Shown in:** Dashboard funnel, KPI export
* **Export column:** `purchased_users`

### Product rollups

#### 13) Best Sellers (Units)

* **Name:** Best Sellers (Units)
* **Type:** Count per product
* **Definition:** Total units sold per product in the window.
* **Source:** Snapshot-driven product rollups
* **Shown in:** Dashboard product chart, products CSV export

#### 14) Best Sellers (Revenue)

* **Name:** Best Sellers (Revenue)
* **Type:** Currency per product
* **Definition:** Total gross paid revenue per product in the window (as derived by product rollups).
* **Source:** Snapshot-driven product rollups
* **Shown in:** Dashboard product chart, products CSV export
* **Clarification (prevents buyer ambiguity):** Product rollup “Revenue” is derived from paid order totals attributable to products via the platform’s product rollup logic (i.e., allocation from order items / units). It is not a separate Stripe ledger and must reconcile to snapshot revenue within expected aggregation rules.

## Export schemas (contract)

These schemas are contractual for buyer-readiness. Any change requires:

1. Updating this document, and
2. Updating/adding a test, and
3. A note in `docs/STATUS.md` (and release note/tag when applicable).

**Machine-checkable contract (authoritative):** `docs/contracts/kpi_contract.json`

Tests must validate export headers against this file to prevent silent drift.

### KPI Summary Export (`analytics-export-kpi-summary`)

* One row per requested window
* Columns:

  * `window_days`
  * `latest_snapshot_day`
  * `revenue`
  * `orders`
  * `aov`
  * `refunded_amount`
  * `refunded_orders`
  * `refund_rate_orders_pct`
  * `unique_customers`
  * `repeat_customers`
  * `repeat_rate_pct`
  * `wishlisted_users`
  * `purchased_users`

### Orders Export (`analytics-export-orders`)

* Source: raw orders within the window (paid/fulfilled)
* Columns:

  * `OrderID`
  * `Email`
  * `Total`
  * `Status`
  * `CreatedAt`
  * `RefundStatus`
  * `RefundPennies`
  * `RefundedAt`
* Notes:

  * `RefundPennies` is the raw stored integer amount (minor units). Any currency formatting is presentation-only.

### Products Export (`analytics-export-products`)

* Source: snapshot-driven product rollups
* Columns:

  * `Product`
  * `Units`
  * `Revenue`

### Customers Export (`analytics-export-customers`)

* Source: raw orders aggregation within window
* Columns:

  * `Email`
  * `Orders`
  * `TotalSpent`

## Subscription metrics policy (avoid over-claiming)

If subscription KPIs are shown anywhere, they must be defined here and must match code.
Until subscription KPIs are snapshot-backed and clearly defined, treat subscription charts as:

* **Operational visibility** only, not decision-grade financial metrics.

## Change control

* Any dashboard KPI change requires updating this file and updating/adding a test.
* Any export schema change requires a note in `docs/STATUS.md` and, for buyer-readiness, a version tag/release note.
