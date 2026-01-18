from __future__ import annotations

from decimal import Decimal

from django.db import models


class AnalyticsSnapshotDaily(models.Model):
    day = models.DateField(unique=True)

    # commerce KPIs
    revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    orders = models.PositiveIntegerField(default=0)
    aov = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    refunded_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    refunded_orders = models.PositiveIntegerField(default=0)

    unique_customers = models.PositiveIntegerField(default=0)
    repeat_customers = models.PositiveIntegerField(default=0)

    # funnel
    wish_users = models.PositiveIntegerField(default=0)
    purchased_users = models.PositiveIntegerField(default=0)

    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-day"]

    def __str__(self) -> str:
        return f"Snapshot {self.day}"


class AnalyticsProductDaily(models.Model):
    """
    Daily rollup per product for best-seller analytics (units + revenue).
    """

    day = models.DateField()
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="daily_analytics"
    )

    units = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("day", "product"),)
        indexes = [
            models.Index(fields=["day"]),
            models.Index(fields=["product"]),
            models.Index(fields=["day", "product"]),
        ]
        ordering = ["-day", "-revenue"]

    def __str__(self) -> str:
        return f"{self.day} product={self.product_id} units={self.units}"
