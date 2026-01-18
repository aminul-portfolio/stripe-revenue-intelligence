from __future__ import annotations

from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from analyticsapp.models import AnalyticsProductDaily
from products.models import Product


def top_products_rollup(days: int, limit: int = 10):
    """
    Best sellers from daily rollups WITHOUT slicing (slicing breaks annotate/order_by).

    We compute a date window [start_day, end_day] and aggregate within it.
    Product label is resolved via Product.__str__ (field-agnostic: works for name/title).
    """
    end_day = timezone.localdate()
    start_day = end_day - timedelta(days=days - 1)

    rows = (
        AnalyticsProductDaily.objects.filter(day__range=(start_day, end_day))
        .values("product_id")
        .annotate(units=Sum("units"), revenue=Sum("revenue"))
        .order_by("-revenue")[:limit]
    )

    product_ids = [r["product_id"] for r in rows]
    products = Product.objects.in_bulk(product_ids)

    out = []
    for r in rows:
        p = products.get(r["product_id"])
        out.append(
            {
                "product_name": str(p) if p else f"Product #{r['product_id']}",
                "units": r["units"] or 0,
                "revenue": r["revenue"] or 0,
            }
        )
    return out
