from django.db.models import Count
from orders.models import Order


COMPLETED_STATUSES = ("paid", "fulfilled")


def customer_kpis(start, end):
    customers = (
        Order.objects.filter(
            status__in=COMPLETED_STATUSES, created_at__range=(start, end)
        )
        .values("email")
        .annotate(orders=Count("id"))
    )
    unique = customers.count()
    repeat = customers.filter(orders__gt=1).count()
    repeat_rate = (repeat / unique * 100) if unique else 0.0

    return {
        "unique": unique,
        "repeat": repeat,
        "repeat_rate": round(repeat_rate, 2),
    }
