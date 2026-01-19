import csv
import json
from decimal import Decimal

from audit.services.logger import log_event
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.decorators import role_required
from analyticsapp.models import AnalyticsSnapshotDaily
from orders.models import Order

from .services.products_rollup import top_products_rollup
from .services.snapshots import snapshot_kpis
from .services.subscriptions import churn_timeseries, subscription_kpis


def _compute_refund_rate_value_pct(
    *, revenue: Decimal, refund_amount: Decimal
) -> Decimal:
    if not revenue or revenue == 0:
        return Decimal("0.00")
    return (Decimal(refund_amount) / Decimal(revenue) * Decimal("100.00")).quantize(
        Decimal("0.01")
    )


@role_required("analyst", "ops", staff_only=True)
def dashboard(request):
    days = int(request.GET.get("days", 30))
    days = days if days in (7, 30, 90) else 30

    # --- Snapshot KPIs (calendar-window based + completeness meta) ---
    snap = snapshot_kpis(days)
    meta = snap.get("meta", {})
    rev = snap["rev"]
    cust = snap["cust"]
    funnel = snap["funnel"]
    daily = snap.get("daily", [])

    snapshots_incomplete = not meta.get("is_complete", False)
    snapshots_missing_days = int(meta.get("missing_days", 0))

    # Optional: compute extra KPI that your updated HTML can show
    rev["refund_rate_value"] = _compute_refund_rate_value_pct(
        revenue=rev.get("revenue", Decimal("0.00")),
        refund_amount=rev.get("refund_amount", Decimal("0.00")),
    )

    # Latest snapshot day (for staleness banner)
    latest = AnalyticsSnapshotDaily.objects.order_by("-day").first()
    latest_snapshot_day = latest.day if latest else None

    # Treat snapshots as stale if latest snapshot is older than yesterday.
    if latest_snapshot_day:
        snapshots_stale = latest_snapshot_day < (
            timezone.localdate() - timezone.timedelta(days=1)
        )
    else:
        snapshots_stale = True

    # --- Products (snapshot-driven rollups) ---
    prod = top_products_rollup(days, limit=10)

    # --- Subs still live for now ---
    start = timezone.now() - timezone.timedelta(days=days)
    end = timezone.now()
    subs = subscription_kpis(start, end)
    churn = churn_timeseries()

    # --- Daily charts (from snapshots) ---
    daily_x = [str(r["day"]) for r in daily]
    revenue_y = [float(r["revenue"] or 0) for r in daily]
    refunds_y = [float(r["refunded_amount"] or 0) for r in daily]
    orders_y = [int(r["orders"] or 0) for r in daily]

    revenue_daily_line = {
        "data": [
            {"type": "scatter", "mode": "lines+markers", "x": daily_x, "y": revenue_y}
        ],
        "layout": {
            "title": f"Revenue Trend (Daily) — {days}d",
            "margin": {"t": 40, "l": 50, "r": 20, "b": 60},
        },
    }

    orders_daily_line = {
        "data": [
            {"type": "scatter", "mode": "lines+markers", "x": daily_x, "y": orders_y}
        ],
        "layout": {
            "title": f"Orders Trend (Daily) — {days}d",
            "margin": {"t": 40, "l": 50, "r": 20, "b": 60},
        },
    }

    refunds_daily_line = {
        "data": [
            {"type": "scatter", "mode": "lines+markers", "x": daily_x, "y": refunds_y}
        ],
        "layout": {
            "title": f"Refunds Trend (Daily) — {days}d",
            "margin": {"t": 40, "l": 50, "r": 20, "b": 60},
        },
    }

    # --- Product charts (snapshot-driven) ---
    product_units_bar = {
        "data": [
            {
                "type": "bar",
                "x": [p["product_name"] for p in prod],
                "y": [float(p["units"] or 0) for p in prod],
            }
        ],
        "layout": {
            "title": "Best Sellers (Units)",
            "margin": {"t": 40, "l": 40, "r": 20, "b": 80},
        },
    }

    product_rev_bar = {
        "data": [
            {
                "type": "bar",
                "x": [p["product_name"] for p in prod],
                "y": [float(p["revenue"] or 0) for p in prod],
            }
        ],
        "layout": {
            "title": "Best Sellers (Revenue)",
            "margin": {"t": 40, "l": 40, "r": 20, "b": 80},
        },
    }

    # --- Churn line (monthly, live) ---
    churn_x = [str(r["month"].date()) for r in churn if r.get("month")]
    churn_y = [r["count"] for r in churn if r.get("month")]
    churn_line = {
        "data": [
            {"type": "scatter", "mode": "lines+markers", "x": churn_x, "y": churn_y}
        ],
        "layout": {
            "title": "Subscription Activity (Monthly)",
            "margin": {"t": 40, "l": 40, "r": 20, "b": 60},
        },
    }

    # --- Funnel ---
    funnel_fig = {
        "data": [
            {
                "type": "funnel",
                "y": ["Wishlisted Users", "Purchased Users"],
                "x": [funnel["wish_users"], funnel["purchased_users"]],
            }
        ],
        "layout": {
            "title": "Wishlist → Purchase Funnel",
            "margin": {"t": 40, "l": 60, "r": 20, "b": 40},
        },
    }

    context = {
        "days": days,
        "rev": rev,
        "cust": cust,
        "subs": subs,
        "latest_snapshot_day": latest_snapshot_day,
        "snapshots_stale": snapshots_stale,
        "snapshots_incomplete": snapshots_incomplete,
        "snapshots_missing_days": snapshots_missing_days,
        "revenue_daily_line_json": json.dumps(revenue_daily_line),
        "orders_daily_line_json": json.dumps(orders_daily_line),
        "refunds_daily_line_json": json.dumps(refunds_daily_line),
        "product_units_bar_json": json.dumps(product_units_bar),
        "product_rev_bar_json": json.dumps(product_rev_bar),
        "churn_line_json": json.dumps(churn_line),
        "funnel_json": json.dumps(funnel_fig),
    }
    return render(request, "analytics/dashboard.html", context)


@role_required("analyst", "ops", staff_only=True)
def export_kpi_summary_csv(request):
    """
    Snapshot-based KPI export (fast, defensible).
    One row output for the requested window.
    """
    days = int(request.GET.get("days", 30))
    days = days if days in (7, 30, 90) else 30

    log_event(
        event_type="analytics_export",
        entity_type="kpi_summary_csv",
        entity_id=f"{days}d",
        user=request.user,
        metadata={"days": days},
    )

    snap = snapshot_kpis(days)
    rev = snap["rev"]
    cust = snap["cust"]
    funnel = snap["funnel"]

    latest = AnalyticsSnapshotDaily.objects.order_by("-day").first()
    latest_snapshot_day = latest.day.isoformat() if latest else ""

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="kpi_summary_{days}d.csv"'
    w = csv.writer(response)

    w.writerow(
        [
            "window_days",
            "latest_snapshot_day",
            "revenue",
            "orders",
            "aov",
            "refunded_amount",
            "refunded_orders",
            "refund_rate_orders_pct",
            "unique_customers",
            "repeat_customers",
            "repeat_rate_pct",
            "wishlisted_users",
            "purchased_users",
        ]
    )

    w.writerow(
        [
            days,
            latest_snapshot_day,
            rev.get("revenue", Decimal("0.00")),
            rev.get("orders", 0),
            rev.get("aov", Decimal("0.00")),
            rev.get("refund_amount", Decimal("0.00")),
            rev.get("refunded_orders", 0),
            rev.get("refund_rate_orders", 0),
            cust.get("unique", 0),
            cust.get("repeat", 0),
            cust.get("repeat_rate", 0),
            funnel.get("wish_users", 0),
            funnel.get("purchased_users", 0),
        ]
    )

    return response


@role_required("analyst", "ops", staff_only=True)
def export_orders_csv(request):
    days = int(request.GET.get("days", 30))
    days = days if days in (7, 30, 90) else 30

    log_event(
        event_type="analytics_export",
        entity_type="orders_csv",
        entity_id=f"{days}d",
        user=request.user,
        metadata={"days": days},
    )

    # Export is still raw orders for the window; snapshot mismatch check will guard this.
    start = timezone.now() - timezone.timedelta(days=days)
    end = timezone.now()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="orders_paid_{days}d.csv"'
    w = csv.writer(response)
    w.writerow(
        [
            "OrderID",
            "Email",
            "Total",
            "Status",
            "CreatedAt",
            "RefundStatus",
            "RefundPennies",
            "RefundedAt",
        ]
    )

    qs = Order.objects.filter(
        status__in=("paid", "fulfilled"), created_at__range=(start, end)
    ).order_by("-created_at")[:5000]
    for o in qs:
        w.writerow(
            [
                o.id,
                o.email,
                o.total,
                o.status,
                o.created_at.isoformat(),
                o.refund_status,
                o.refund_amount_pennies,
                o.refunded_at.isoformat() if o.refunded_at else "",
            ]
        )
    return response


@role_required("analyst", "ops", staff_only=True)
def export_products_csv(request):
    days = int(request.GET.get("days", 30))
    days = days if days in (7, 30, 90) else 30

    log_event(
        event_type="analytics_export",
        entity_type="products_csv",
        entity_id=f"{days}d",
        user=request.user,
        metadata={"days": days},
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="best_sellers_{days}d.csv"'
    w = csv.writer(response)
    w.writerow(["Product", "Units", "Revenue"])

    rows = top_products_rollup(days, limit=5000)
    for r in rows:
        w.writerow([r["product_name"], r["units"], r["revenue"]])

    return response


@role_required("analyst", "ops", staff_only=True)
def export_customers_csv(request):
    days = int(request.GET.get("days", 30))
    days = days if days in (7, 30, 90) else 30

    log_event(
        event_type="analytics_export",
        entity_type="customers_csv",
        entity_id=f"{days}d",
        user=request.user,
        metadata={"days": days},
    )

    start = timezone.now() - timezone.timedelta(days=days)
    end = timezone.now()

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="customers_{days}d.csv"'
    w = csv.writer(response)
    w.writerow(["Email", "Orders", "TotalSpent"])

    qs = (
        Order.objects.filter(
            status__in=("paid", "fulfilled"), created_at__range=(start, end)
        )
        .values("email")
        .annotate(orders=Count("id"), total_spent=Sum("total"))
        .order_by("-total_spent")[:5000]
    )
    for r in qs:
        w.writerow([r["email"], r["orders"], r["total_spent"]])

    return response
