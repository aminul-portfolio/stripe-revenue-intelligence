from django.db import models
from django.conf import settings


class DataQualityIssue(models.Model):
    ISSUE_TYPES = (
        ("payment_mismatch", "Payment mismatch"),
        ("missing_stripe_ref", "Missing Stripe reference"),
        ("stock_anomaly", "Stock anomaly"),
        ("invalid_order_state", "Invalid order state"),
        ("amount_mismatch", "Amount mismatch"),
        (
            "analytics_snapshot_reconciliation",
            "Analytics snapshot reconciliation",
        ),  # ✅ add
    )

    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPES)
    reference_id = models.CharField(max_length=255)  # stable key like "order:123"
    description = models.TextField()

    status = models.CharField(
        max_length=20,
        default="open",
        choices=(("open", "Open"), ("resolved", "Resolved")),
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("issue_type", "reference_id")

    def __str__(self):
        return f"{self.issue_type} {self.reference_id} ({self.status})"
