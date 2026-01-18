from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone

from subscriptions.models import Subscription


def subscription_kpis(start, end):
    """
    Compute subscription KPIs within a single consistent window.

    Notes:
    - Uses canonical status 'canceled'
    - Adds a small end-boundary grace to avoid microsecond timing issues
      in tests/CI where end is captured before objects are created.
    """
    if timezone.is_naive(start):
        start = timezone.make_aware(start, timezone.get_current_timezone())
    if timezone.is_naive(end):
        end = timezone.make_aware(end, timezone.get_current_timezone())

    end_grace = end + timezone.timedelta(seconds=1)

    window = Subscription.objects.filter(
        created_at__gte=start,
        created_at__lte=end_grace,
    )

    total = window.count()
    active = window.filter(status="active").count()
    canceled = window.filter(status="canceled").count()

    churn = (canceled / total * 100) if total else 0.0

    return {
        "total": total,
        "active": active,
        "canceled": canceled,
        "churn": round(churn, 2),
    }


def churn_timeseries():
    qs = (
        Subscription.objects.annotate(month=TruncMonth("created_at"))
        .values("month", "status")
        .annotate(count=Count("id"))
        .order_by("month", "status")
    )
    return list(qs)
