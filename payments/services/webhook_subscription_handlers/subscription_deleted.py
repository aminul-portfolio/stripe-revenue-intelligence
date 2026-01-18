from __future__ import annotations

from datetime import timezone as dt_timezone
from typing import Optional

from django.db import transaction
from django.utils import timezone

from subscriptions.models import Subscription


def _dt_from_unix(ts: Optional[int]):
    if not ts:
        return None
    return timezone.datetime.fromtimestamp(int(ts), tz=dt_timezone.utc)


@transaction.atomic
def handle_customer_subscription_deleted(*, subscription: dict) -> None:
    sub_id = (subscription.get("id") or "").strip()
    if not sub_id:
        return

    ended_at = _dt_from_unix(subscription.get("ended_at")) or timezone.now()
    canceled_at = _dt_from_unix(subscription.get("canceled_at")) or timezone.now()

    row = (
        Subscription.objects.select_for_update()
        .filter(stripe_subscription_id=sub_id)
        .first()
    )
    if not row:
        return

    row.status = "canceled"
    row.ended_at = ended_at
    row.canceled_at = canceled_at
    row.cancel_at_period_end = False
    row.mrr_pennies = 0
    row.save(
        update_fields=[
            "status",
            "ended_at",
            "canceled_at",
            "cancel_at_period_end",
            "mrr_pennies",
            "updated_at",
        ]
    )
