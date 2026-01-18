from __future__ import annotations

from decimal import Decimal
from datetime import datetime, time, timedelta

from django.db import models  # <-- add this line
from django.utils import timezone

from analyticsapp.models import AnalyticsSnapshotDaily
from orders.models import Order


def analytics_snapshot_reconciliation(
    *, days: int = 30, tolerance_pounds: Decimal = Decimal("0.50")
) -> list[dict]:
    """
    Compare snapshot totals vs raw Orders for the same window.

    Returns issues list; empty means pass.
    """
    today = timezone.localdate()
    start_day = today - timedelta(days=days - 1)

    # Snapshot aggregates
    snap_qs = AnalyticsSnapshotDaily.objects.filter(day__range=(start_day, today))
    snap_agg = snap_qs.aggregate(
        revenue_sum=models.Sum("revenue"),
        orders_sum=models.Sum("orders"),
    )
    snap_revenue = snap_agg["revenue_sum"] or Decimal("0.00")
    snap_orders = int(snap_agg["orders_sum"] or 0)

    # Raw orders aggregates (paid+fulfilled only)
    tz = timezone.get_current_timezone()
    start_dt = timezone.make_aware(datetime.combine(start_day, time.min), tz)
    end_dt = timezone.make_aware(
        datetime.combine(today + timedelta(days=1), time.min), tz
    )

    raw_qs = Order.objects.filter(
        status__in=("paid", "fulfilled"),
        created_at__gte=start_dt,
        created_at__lt=end_dt,
    )

    raw_agg = raw_qs.aggregate(
        revenue_sum=models.Sum("total"),
        orders_sum=models.Count("id"),
    )
    raw_revenue = raw_agg["revenue_sum"] or Decimal("0.00")
    raw_orders = int(raw_agg["orders_sum"] or 0)

    issues: list[dict] = []

    revenue_diff = (raw_revenue - snap_revenue).copy_abs()
    orders_diff = abs(raw_orders - snap_orders)

    if revenue_diff > tolerance_pounds or orders_diff > 0:
        issues.append(
            {
                "issue_type": "analytics_snapshot_reconciliation",
                "severity": "high" if revenue_diff > tolerance_pounds else "medium",
                "title": "Analytics snapshot totals do not match raw orders",
                "details": {
                    "days": days,
                    "tolerance_pounds": str(tolerance_pounds),
                    "snapshot_revenue": str(snap_revenue),
                    "raw_revenue": str(raw_revenue),
                    "revenue_diff": str(revenue_diff),
                    "snapshot_orders": snap_orders,
                    "raw_orders": raw_orders,
                    "orders_diff": orders_diff,
                },
            }
        )

    return issues
