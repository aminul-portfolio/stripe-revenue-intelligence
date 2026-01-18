from __future__ import annotations

from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from analyticsapp.models import AnalyticsSnapshotDaily
from monitoring.models import DataQualityIssue
from orders.models import Order


ISSUE_TYPE = "analytics_snapshot_reconciliation"


def run_analytics_snapshot_reconciliation(
    *, days: int = 30, tolerance_pounds: Decimal = Decimal("0.50")
) -> None:
    """
    Compare AnalyticsSnapshotDaily totals vs raw paid/fulfilled Orders totals
    for the same window. Creates/updates a DataQualityIssue if mismatch exceeds tolerance.
    Auto-resolves any previously open issue when the window matches.
    """
    today = timezone.localdate()
    start_day = today - timedelta(days=days - 1)
    reference_id = f"analytics:snapshot_recon:{days}d"

    # --- Snapshot aggregates ---
    snap_qs = AnalyticsSnapshotDaily.objects.filter(day__range=(start_day, today))
    snap_days = snap_qs.count()

    snap_agg = snap_qs.aggregate(
        revenue_sum=models.Sum("revenue"),
        orders_sum=models.Sum("orders"),
    )
    snap_revenue = snap_agg["revenue_sum"] or Decimal("0.00")
    snap_orders = int(snap_agg["orders_sum"] or 0)

    # Guard: snapshots missing (avoid false mismatches)
    if snap_days < days:
        DataQualityIssue.objects.update_or_create(
            issue_type=ISSUE_TYPE,
            reference_id=reference_id,
            defaults={
                "description": (
                    f"Snapshots incomplete: expected {days} day(s), found {snap_days}. "
                    f"Run: python manage.py build_analytics_snapshots --days {days}"
                ),
                "status": "open",
                "resolved_at": None,
            },
        )
        return

    # --- Raw aggregates (paid + fulfilled) ---
    start_dt = timezone.make_aware(datetime.combine(start_day, time.min))
    end_dt = timezone.make_aware(datetime.combine(today, time.max))

    raw_agg = Order.objects.filter(
        status__in=("paid", "fulfilled"),
        created_at__range=(start_dt, end_dt),
    ).aggregate(
        revenue_sum=models.Sum("total"),
        orders_sum=models.Count("id"),
    )
    raw_revenue = raw_agg["revenue_sum"] or Decimal("0.00")
    raw_orders = int(raw_agg["orders_sum"] or 0)

    revenue_diff = (raw_revenue - snap_revenue).copy_abs()
    orders_diff = abs(raw_orders - snap_orders)

    if revenue_diff > tolerance_pounds or orders_diff != 0:
        DataQualityIssue.objects.update_or_create(
            issue_type=ISSUE_TYPE,
            reference_id=reference_id,
            defaults={
                "description": (
                    f"Snapshot vs raw mismatch for {days}d window. "
                    f"snapshot_revenue={snap_revenue}, raw_revenue={raw_revenue}, diff={revenue_diff}. "
                    f"snapshot_orders={snap_orders}, raw_orders={raw_orders}, orders_diff={orders_diff}. "
                    f"tolerance_pounds={tolerance_pounds}."
                ),
                "status": "open",
                "resolved_at": None,
            },
        )
        return

    # Resolve if previously open
    DataQualityIssue.objects.filter(
        issue_type=ISSUE_TYPE, reference_id=reference_id, status="open"
    ).update(
        status="resolved",
        resolved_at=timezone.now(),
    )
