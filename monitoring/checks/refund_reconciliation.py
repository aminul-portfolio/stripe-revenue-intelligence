from __future__ import annotations

from django.db.models import Q

from monitoring.models import DataQualityIssue
from orders.models import Order
from payments.models import StripeEvent


ISSUE_TYPE = "refund_not_applied"


def run_refund_reconciliation() -> None:
    """
    Create issues when Stripe processed a refund event but Order refund fields
    are still not updated.
    """
    # Pull recent processed refund events
    events = StripeEvent.objects.filter(
        event_type="charge.refunded",
        status="processed",
    ).order_by("-processed_at")[:5000]

    refunded_charge_ids = set()
    charge_refund_map = {}  # charge_id -> amount_refunded

    for ev in events:
        obj = (ev.payload or {}).get("data", {}).get("object", {}) or {}
        charge_id = obj.get("id") or ""
        amount_refunded = int(obj.get("amount_refunded") or 0)
        if charge_id and amount_refunded > 0:
            refunded_charge_ids.add(charge_id)
            charge_refund_map[charge_id] = amount_refunded

    if not refunded_charge_ids:
        return

    # Orders where Stripe indicates refund, but local fields show none
    qs = Order.objects.filter(stripe_charge_id__in=refunded_charge_ids).filter(
        Q(refund_status="none") | Q(refund_amount_pennies=0)
    )

    for o in qs.iterator():
        DataQualityIssue.objects.get_or_create(
            issue_type=ISSUE_TYPE,
            entity_type="order",
            entity_id=str(o.id),
            status="open",
            defaults={
                "summary": "Stripe refund exists but order refund fields not updated.",
                "details": {
                    "order_id": o.id,
                    "stripe_charge_id": o.stripe_charge_id,
                    "stripe_amount_refunded": charge_refund_map.get(o.stripe_charge_id),
                    "refund_status": o.refund_status,
                    "refund_amount_pennies": o.refund_amount_pennies,
                },
            },
        )
