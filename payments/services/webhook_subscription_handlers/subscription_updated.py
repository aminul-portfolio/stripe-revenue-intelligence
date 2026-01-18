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


def _extract_price_and_mrr(subscription: dict) -> tuple[str, int]:
    """
    Returns (price_id, mrr_pennies) from first subscription item.
    mrr_pennies is best-effort:
      - month: unit_amount / interval_count
      - year: unit_amount / 12 / interval_count
      - else: unit_amount
    """
    price_id = ""
    mrr_pennies = 0

    try:
        item0 = ((subscription.get("items") or {}).get("data") or [])[0]
        price = item0.get("price") or {}
        price_id = price.get("id") or ""

        unit_amount = int(price.get("unit_amount") or 0)
        recurring = price.get("recurring") or {}
        interval = recurring.get("interval")
        interval_count = int(recurring.get("interval_count") or 1)

        if interval == "month":
            mrr_pennies = int(unit_amount / max(interval_count, 1))
        elif interval == "year":
            mrr_pennies = int(unit_amount / 12 / max(interval_count, 1))
        else:
            mrr_pennies = unit_amount
    except Exception:
        pass

    return price_id, mrr_pennies


@transaction.atomic
def handle_customer_subscription_updated(*, subscription: dict) -> None:
    sub_id = (subscription.get("id") or "").strip()
    if not sub_id:
        return

    status = (subscription.get("status") or "incomplete").strip()
    cancel_at_period_end = bool(subscription.get("cancel_at_period_end") or False)

    cps = _dt_from_unix(subscription.get("current_period_start"))
    cpe = _dt_from_unix(subscription.get("current_period_end"))
    canceled_at = _dt_from_unix(subscription.get("canceled_at"))
    ended_at = _dt_from_unix(subscription.get("ended_at"))

    price_id, mrr_pennies = _extract_price_and_mrr(subscription)

    row = (
        Subscription.objects.select_for_update()
        .filter(stripe_subscription_id=sub_id)
        .first()
    )
    if not row:
        # Only sync existing local subscriptions here.
        # Local row creation happens in your "create subscription" flow.
        return

    updates = {
        "status": status,
        "cancel_at_period_end": cancel_at_period_end,
        "current_period_start": cps,
        "current_period_end": cpe,
        "canceled_at": canceled_at,
        "ended_at": ended_at,
        "mrr_pennies": mrr_pennies,
    }
    if price_id:
        updates["stripe_price_id"] = price_id

    for k, v in updates.items():
        setattr(row, k, v)

    row.save(update_fields=list(updates.keys()) + ["updated_at"])
