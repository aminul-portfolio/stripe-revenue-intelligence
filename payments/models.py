from django.db import models
from decimal import Decimal


class StripeEvent(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        default="received",
        choices=[
            ("received", "Received"),
            ("processed", "Processed"),
            ("ignored", "Ignored"),
            ("failed", "Failed"),
        ],
    )

    class Meta:
        indexes = [
            models.Index(fields=["event_type", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.event_id})"

    @property
    def mrr_gbp(self) -> Decimal:
        # pennies -> pounds
        return (Decimal(self.mrr_pennies or 0) / Decimal("100")).quantize(
            Decimal("0.01")
        )
