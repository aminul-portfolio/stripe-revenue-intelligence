from django.db.models import Count
from django.db.models.functions import TruncMonth
from subscriptions.models import Subscription


def subscription_kpis(start, end):
    # Total subscriptions CREATED in the window (all statuses)
    in_window = Subscription.objects.filter(created_at__range=(start, end))

    total = in_window.count()
    active = in_window.filter(status="active").count()
    canceled = in_window.filter(status="canceled").count()

    churn = (canceled / total * 100) if total else 0

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
        .order_by("month")
    )
    return list(qs)
