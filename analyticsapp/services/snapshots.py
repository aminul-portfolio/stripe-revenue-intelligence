from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone

from analyticsapp.models import AnalyticsSnapshotDaily


def snapshot_kpis(days: int) -> dict:
    """
    Return window KPIs aggregated from daily snapshots for the LAST N CALENDAR DAYS.

    Always returns:
      - rev, cust, funnel
      - daily: list of dicts for charts (day, revenue, orders, refunded_amount)
      - meta: completeness + date window info

    Meta fields:
      - start_day / end_day: calendar window boundaries (inclusive)
      - snap_days: how many snapshot rows exist in that window
      - is_complete: True iff snap_days == days
      - missing_days: max(days - snap_days, 0)
    """
    if days < 1:
        days = 1

    end_day = timezone.localdate()
    start_day = end_day - timedelta(days=days - 1)

    qs = AnalyticsSnapshotDaily.objects.filter(day__range=(start_day, end_day))
    snap_days = qs.count()
    is_complete = snap_days == days
    missing_days = max(days - snap_days, 0)

    agg = qs.aggregate(
        revenue=Sum("revenue"),
        orders=Sum("orders"),
        refunded_amount=Sum("refunded_amount"),
        refunded_orders=Sum("refunded_orders"),
        unique_customers=Sum("unique_customers"),
        repeat_customers=Sum("repeat_customers"),
        wish_users=Sum("wish_users"),
        purchased_users=Sum("purchased_users"),
    )

    daily = list(
        qs.order_by("day").values("day", "revenue", "orders", "refunded_amount")
    )

    revenue = agg["revenue"] or Decimal("0.00")
    orders = int(agg["orders"] or 0)

    # AOV should be computed as revenue / orders (not average of daily AOV)
    aov = (revenue / orders).quantize(Decimal("0.01")) if orders else Decimal("0.00")

    refunded_orders = int(agg["refunded_orders"] or 0)
    refund_amount = agg["refunded_amount"] or Decimal("0.00")
    refund_rate_orders = (
        (Decimal(refunded_orders) / Decimal(orders) * 100) if orders else Decimal("0")
    )

    unique = int(agg["unique_customers"] or 0)
    repeat = int(agg["repeat_customers"] or 0)
    repeat_rate = round((repeat / unique * 100), 2) if unique else 0.0

    return {
        "meta": {
            "start_day": start_day,
            "end_day": end_day,
            "snap_days": snap_days,
            "is_complete": is_complete,
            "missing_days": missing_days,
        },
        "rev": {
            "revenue": revenue,
            "orders": orders,
            "aov": aov,
            "refund_amount": refund_amount,
            "refunded_orders": refunded_orders,
            "refund_rate_orders": round(refund_rate_orders, 2),
        },
        "cust": {
            "unique": unique,
            "repeat": repeat,
            "repeat_rate": repeat_rate,
        },
        "funnel": {
            "wish_users": int(agg["wish_users"] or 0),
            "purchased_users": int(agg["purchased_users"] or 0),
        },
        "daily": daily,
    }
