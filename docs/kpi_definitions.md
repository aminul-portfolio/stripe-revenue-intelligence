# KPI Definitions — Revenue Intelligence for Stripe Commerce

**Purpose:** This document is the single source of truth for KPI meanings, formulas, windows, filters, and sources.
**Rule:** Every KPI shown in dashboards/exports must be defined here and must match implementation.

---

## 1) Time windows and data sources

### 1.1 Calendar window convention (authoritative)

All window KPIs are computed for the **last N calendar days**, inclusive:

* `end_day = timezone.localdate()`
* `start_day = end_day - (days - 1)`

**Implication:** A 7-day window includes exactly 7 calendar dates (not “last 7*24 hours”).

### 1.2 Snapshot system (authoritative for dashboards)

Dashboards should read KPIs from **daily snapshots**, not from raw orders in real time.

**Primary model:** `analyticsapp.models.AnalyticsSnapshotDaily`
**Primary service:** `analyticsapp/services/snapshots.py::snapshot_kpis(days)`

### 1.3 Snapshot completeness metadata

The snapshot service returns:

* `meta.start_day`: inclusive start date for window
* `meta.end_day`: inclusive end date for window
* `meta.snap_days`: snapshot rows present in window
* `meta.is_complete`: `snap_days == days`
* `meta.missing_days`: `max(days - snap_days, 0)`

---

## 2) Revenue KPIs (rev)

All revenue KPIs below are **aggregated from `AnalyticsSnapshotDaily`** in the selected window.

### 2.1 Revenue

**Definition:** Total recognized revenue for the selected window as recorded in snapshots.

* **Formula:** `revenue = SUM(AnalyticsSnapshotDaily.revenue)`
* **Window:** last N calendar days (inclusive), by snapshot `day`
* **Filters:** `AnalyticsSnapshotDaily.day BETWEEN start_day AND end_day`
* **Source of truth:** `AnalyticsSnapshotDaily.revenue`

**Notes / contract:**

* This is the value used for reporting in the dashboard.
* The exact “recognition timing” depends on how snapshots are built (see snapshot builder docs/command).

### 2.2 Orders

**Definition:** Count of orders included in snapshots for the selected window.

* **Formula:** `orders = SUM(AnalyticsSnapshotDaily.orders)`
* **Window:** last N calendar days (inclusive)
* **Filters:** snapshot `day` range filter only
* **Source of truth:** `AnalyticsSnapshotDaily.orders`

### 2.3 AOV (Average Order Value)

**Definition:** Average order value computed from window totals (not averaged daily).

* **Formula:** `aov = revenue / orders` (if `orders > 0`, else `0.00`)
* **Window:** last N calendar days (inclusive)
* **Source of truth:** computed in `analyticsapp/services/snapshots.py::snapshot_kpis`

### 2.4 Refund amount

**Definition:** Total refunded amount recorded in snapshots for the selected window.

* **Formula:** `refund_amount = SUM(AnalyticsSnapshotDaily.refunded_amount)`
* **Window:** last N calendar days (inclusive)
* **Source of truth:** `AnalyticsSnapshotDaily.refunded_amount`

### 2.5 Refunded orders

**Definition:** Count of refunded orders recorded in snapshots for the selected window.

* **Formula:** `refunded_orders = SUM(AnalyticsSnapshotDaily.refunded_orders)`
* **Window:** last N calendar days (inclusive)
* **Source of truth:** `AnalyticsSnapshotDaily.refunded_orders`

### 2.6 Refund rate (orders %)

**Definition:** Percentage of orders that were refunded, based on order counts.

* **Formula:** `refund_rate_orders = (refunded_orders / orders) * 100` (if `orders > 0`, else `0`)
* **Window:** last N calendar days (inclusive)
* **Source of truth:** computed in `analyticsapp/services/snapshots.py::snapshot_kpis`

**Notes / contract:**

* This is an **orders-based** refund rate, not a value-based rate.

---

## 3) Customer KPIs (cust)

All customer KPIs below are **aggregated from `AnalyticsSnapshotDaily`** in the selected window.

### 3.1 Unique customers

**Definition:** Number of unique customers counted in snapshots for the window.

* **Formula:** `unique = SUM(AnalyticsSnapshotDaily.unique_customers)`
* **Window:** last N calendar days (inclusive)
* **Source of truth:** `AnalyticsSnapshotDaily.unique_customers`

### 3.2 Repeat customers

**Definition:** Number of repeat customers counted in snapshots for the window.

* **Formula:** `repeat = SUM(AnalyticsSnapshotDaily.repeat_customers)`
* **Window:** last N calendar days (inclusive)
* **Source of truth:** `AnalyticsSnapshotDaily.repeat_customers`

### 3.3 Repeat rate (%)

**Definition:** Percentage of customers who are repeat customers.

* **Formula:** `repeat_rate = (repeat / unique) * 100` (if `unique > 0`, else `0`)
* **Window:** last N calendar days (inclusive)
* **Source of truth:** computed in `analyticsapp/services/snapshots.py::snapshot_kpis`

**Notes / contract:**

* This is defined over snapshot-aggregated totals for the window.
* The meaning of “repeat” depends on snapshot builder logic (e.g., repeat buyer within day or within historical horizon). Ensure snapshot builder aligns with this contract.

---

## 4) Funnel KPIs (wishlist → purchase)

Funnel KPIs are stored in snapshots, and are built from the funnel service.

### 4.1 Completed order statuses (canonical)

For funnel conversion, a “purchase” is defined as an order with status in:

* `("paid", "fulfilled")`

**Source of truth:** `analyticsapp/services/funnel.py::COMPLETED_STATUSES`

### 4.2 Wish users

**Definition:** Distinct users who created at least one wishlist item in the selected window.

* **Formula:**

  * `wish_users = COUNT(DISTINCT Wishlist.user_id)` for `Wishlist.created_at` in window
* **Window:** `Wishlist.created_at` between `start` and `end` (datetime range used by funnel builder)
* **Filters:** `Wishlist.created_at__range=(start, end)`
* **Source of truth:** `analyticsapp/services/funnel.py::wishlist_funnel`

### 4.3 Purchased users

**Definition:** Distinct users who both:

1. are in `wish_users` set for the window, and
2. placed at least one completed order in the same window.

* **Formula:**

  * `purchased_users = COUNT(DISTINCT Order.user_id)`
  * where `Order.status IN ("paid","fulfilled")`
  * and `Order.created_at` in window
  * and `Order.user_id IN wish_users`
* **Window:** `Order.created_at__range=(start, end)` (datetime range used by funnel builder)
* **Source of truth:** `analyticsapp/services/funnel.py::wishlist_funnel`

### 4.4 Funnel conversion rate (optional)

If displayed, define explicitly:

* **Formula:** `conversion_rate = (purchased_users / wish_users) * 100` (if `wish_users > 0`, else `0`)
* **Window:** same as 4.2–4.3

---

## 5) Daily series (charts)

The snapshot service returns `daily` rows for charting:

* **Fields:** `day`, `revenue`, `orders`, `refunded_amount`
* **Formula:** direct snapshot values per day
* **Source of truth:** `AnalyticsSnapshotDaily` values returned by
  `analyticsapp/services/snapshots.py::snapshot_kpis`

---

## 6) Order status canonical spellings

**Canonical order status values (active code):**

* `pending`
* `paid`
* `fulfilled`
* `canceled` (canonical spelling)

**Legacy allowance:** historical narrative/migrations/comments may contain `cancelled`, but active code/tests/docs must use canonical `canceled`.

---

## 7) Implementation references (for reviewers)

* Snapshot KPIs service: `analyticsapp/services/snapshots.py::snapshot_kpis(days)`
* Funnel builder: `analyticsapp/services/funnel.py::wishlist_funnel(start, end)`
* Wishlist model: `wishlist/models.py`
* Orders model/statuses: `orders/models.py`
* Snapshot model: `analyticsapp/models.py` (AnalyticsSnapshotDaily)

---

## 8) Change control

Any KPI change must include:

1. Update this document (definition + formula + sources)
2. Update/extend tests
3. Add proof artifacts under `docs/proof/` for the change date
4. Update `docs/STATUS.md` with KPI contract note
