from django.db.models import Sum
from orders.models import OrderItem


def top_products(start, end, limit=7):
    qs = (
        OrderItem.objects.filter(
            order__status="paid", order__created_at__range=(start, end)
        )
        .values("product_name")
        .annotate(units=Sum("qty"), revenue=Sum("line_total"))
        .order_by("-units")[:limit]
    )
    return list(qs)
