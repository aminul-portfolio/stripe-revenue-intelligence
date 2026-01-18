from __future__ import annotations

from django.db import transaction

from subscriptions.models import Subscription


@transaction.atomic
def handle_invoice_paid(*, invoice: dict) -> None:
    sub_id = (invoice.get("subscription") or "").strip()
    if not sub_id:
        return

    qs = Subscription.objects.select_for_update().filter(stripe_subscription_id=sub_id)
    if not qs.exists():
        return

    row = qs.first()
    # Keep it simple: paid invoice generally means subscription is active/trialing.
    if row.status not in ("active", "trialing"):
        row.status = "active"
        row.save(update_fields=["status", "updated_at"])
