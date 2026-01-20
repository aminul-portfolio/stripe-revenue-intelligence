# KPI Definitions — Revenue Intelligence for Stripe Commerce

This document is the single source of truth for KPI meaning and calculation rules.
Every KPI shown in the dashboard or exports must be defined here and must match implementation.

## Scope and time windows

* Supported windows: **7 / 30 / 90 days**
* KPI values are computed for the selected window.
* Source of truth: **analytics snapshots** for revenue/orders/refunds/funnel/customer metrics where available.

### Time boundaries

* Window is defined as “last N days” relative to `timezone.now()` / `timezone.localdate()` in application timezone.
* Snapshot-driven KPIs use snapshot days; completeness is surfaced in the UI via snapshot metadata (e.g., missing days).

## Data sources (authoritative order)

1. **Analytics snapshots** (daily snapshot rows + derived rollups)
2. **Orders DB** (raw orders within window; used by some exports and reconciliation)
3. **Stripe** (used for live payments/webhooks; reconciliation checks ensure drift is visible)

## KPI glossary

### Revenue KPIs

#### 1) Revenue

* **Name:** Revenue
* **Type:** Currency
* **Definition:** Total paid revenue within the window.
* **Source:** Snapshots
* **Notes:** Revenue is based on paid/fulfilled orders included in snapshots. If snapshot completeness is false, revenue may be understated.
* **Shown in:** Dashboard (overview), KPI export (`kpi_summary_*d.csv`)

#### 2) Orders

* **Name:** Orders
* **Type:** Count
* **Definition:** Number of paid orders within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

#### 3) AOV (Average Order Value)

* **Name:** AOV
* **Type:** Currency
* **Definition:** `Revenue / Orders` for the window (0 if Orders=0).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

### Refund KPIs

#### 4) Refunded Amount

* **Name:** Refunded Amount
* **Type:** Currency
* **Definition:** Total refunded value within the window (monetary).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

#### 5) Refunded Orders

* **Name:** Refunded Orders
* **Type:** Count
* **Definition:** Count of orders that have refunds recorded within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

#### 6) Refund Rate (Orders %)

* **Name:** Refund Rate (Orders %)
* **Type:** Percentage
* **Definition:** `(Refunded Orders / Orders) * 100` (0 if Orders=0).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export
* **Export column:** `refund_rate_orders_pct`

#### 7) Refund Rate (Value %)

* **Name:** Refund Rate (Value %)
* **Type:** Percentage
* **Definition:** `(Refunded Amount / Revenue) * 100` (0 if Revenue=0).
* **Source:** Derived from snapshot KPIs (Revenue + Refunded Amount).
* **Shown in:** Dashboard (if displayed)

### Customer KPIs

#### 8) Unique Customers

* **Name:** Unique Customers
* **Type:** Count
* **Definition:** Number of distinct purchasing customers within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

#### 9) Repeat Customers

* **Name:** Repeat Customers
* **Type:** Count
* **Definition:** Number of customers with 2+ purchases (based on snapshot logic) within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

#### 10) Repeat Rate (%)

* **Name:** Repeat Rate (%)
* **Type:** Percentage
* **Definition:** `(Repeat Customers / Unique Customers) * 100` (0 if Unique Customers=0).
* **Source:** Snapshots
* **Shown in:** Dashboard, KPI export

### Funnel KPIs

#### 11) Wishlisted Users

* **Name:** Wishlisted Users
* **Type:** Count
* **Definition:** Number of distinct users who have at least one wishlist action/state within the window.
* **Source:** Snapshots
* **Shown in:** Dashboard funnel, KPI export

#### 12) Purchased Users

* **Name:** Purchased Users
* **Type:** Count
* **Definition:** Number of distinct users who purchased within the window (as used by funnel logic).
* **Source:** Snapshots
* **Shown in:** Dashboard funnel, KPI export

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
* **Definition:** Total revenue per product in the window.
* **Source:** Snapshot-driven product rollups
* **Shown in:** Dashboard product chart, products CSV export

## Export schemas (contract)

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
