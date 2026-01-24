from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

# Canonical subscription status values (American spelling: "canceled")
# Keeping this explicit ensures the DB-level constraint is stable and predictable.
SUBSCRIPTION_STATUS_VALUES = (
    "incomplete",
    "incomplete_expired",
    "trialing",
    "active",
    "past_due",
    "canceled",
    "unpaid",
    "paused",
)


class Subscription(models.Model):
    class Status(models.TextChoices):
        INCOMPLETE = "incomplete", "Incomplete"
        INCOMPLETE_EXPIRED = "incomplete_expired", "Incomplete Expired"
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELED = "canceled", "Canceled"
        UNPAID = "unpaid", "Unpaid"
        PAUSED = "paused", "Paused"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=220, blank=True)

    stripe_customer_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, db_index=True)
    stripe_price_id = models.CharField(max_length=255, blank=True, db_index=True)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.INCOMPLETE,
        db_index=True,
    )

    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Stored as integer pennies (GBP)
    mrr_pennies = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["stripe_subscription_id"]),
            models.Index(fields=["stripe_customer_id"]),
        ]
        constraints = [
            # DB-level guard: prevents invalid status strings (e.g., "cancelled") from persisting.
            models.CheckConstraint(
                name="subscription_status_valid",
                check=models.Q(status__in=SUBSCRIPTION_STATUS_VALUES),
            ),
        ]

    @property
    def mrr_gbp(self) -> Decimal:
        return (Decimal(self.mrr_pennies or 0) / Decimal("100")).quantize(Decimal("0.01"))

    def mark_canceled_local(self) -> None:
        if not self.canceled_at:
            self.canceled_at = timezone.now()
        self.status = self.Status.CANCELED
        self.save(update_fields=["status", "canceled_at", "updated_at"])


class StripeCustomer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stripe_customer",
    )
    stripe_customer_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user_id} -> {self.stripe_customer_id}"
