from decimal import Decimal

from django.db.models import Avg, Sum, Count
from orders.models import Order


COMPLETED_STATUSES = ("paid", "fulfilled")


def revenue_kpis(start, end):
    paid = Order.objects.filter(
        status__in=COMPLETED_STATUSES, created_at__range=(start, end)
    )

    revenue = paid.aggregate(v=Sum("total"))["v"] or Decimal("0.00")
    orders = paid.count()
    aov = paid.aggregate(v=Avg("total"))["v"] or Decimal("0.00")

    refunded_qs = Order.objects.filter(
        refund_amount_pennies__gt=0,
        refunded_at__isnull=False,
        refunded_at__range=(start, end),
    )
    refunded_orders = refunded_qs.aggregate(v=Count("id"))["v"] or 0
    refunded_pennies = refunded_qs.aggregate(v=Sum("refund_amount_pennies"))["v"] or 0
    refund_amount = (Decimal(refunded_pennies) / Decimal("100")).quantize(
        Decimal("0.01")
    )

    refund_rate_orders = (
        (Decimal(refunded_orders) / Decimal(orders) * 100) if orders else Decimal("0")
    )

    return {
        "revenue": revenue,
        "orders": orders,
        "aov": aov,
        "refunded_orders": refunded_orders,
        "refund_amount": refund_amount,
        "refund_rate_orders": round(refund_rate_orders, 2),
    }
