from django.db import models
from django.conf import settings

from products.models import Product, ProductVariant


class Order(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    )

    REFUND_STATUS = (
        ("none", "None"),
        ("partial", "Partial"),
        ("full", "Full"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    email = models.EmailField()

    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)

    # Sprint 2 (Refunds): tracking fields for Stripe refunds
    refund_status = models.CharField(
        max_length=10, choices=REFUND_STATUS, default="none"
    )
    refund_amount_pennies = models.PositiveIntegerField(default=0)
    refunded_at = models.DateTimeField(null=True, blank=True)

    shipping_name = models.CharField(max_length=120, blank=True)
    shipping_line1 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=120, blank=True)
    shipping_postcode = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=2, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.id} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    # immutable references for inventory + analytics correctness
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.SET_NULL
    )
    variant = models.ForeignKey(
        ProductVariant, null=True, blank=True, on_delete=models.SET_NULL
    )

    product_name = models.CharField(max_length=220)
    sku = models.CharField(max_length=64, blank=True)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product_name} x{self.qty} (Order #{self.order_id})"
