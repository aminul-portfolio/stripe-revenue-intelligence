from __future__ import annotations

from datetime import timezone as dt_timezone
from typing import Optional

import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from audit.services.logger import log_event
from subscriptions.models import Subscription


def _stripe_init() -> None:
    stripe.api_key = settings.STRIPE_SECRET_KEY


def _dt_from_unix(ts: Optional[int]):
    if not ts:
        return None
    return timezone.datetime.fromtimestamp(int(ts), tz=dt_timezone.utc)


@transaction.atomic
def cancel_stripe_subscription(
    *, subscription: Subscription, user=None, at_period_end: bool = True
) -> None:
    """
    Cancel the Stripe subscription.

    Modes:
    - at_period_end=True  => schedule cancellation (still active until period end)
    - at_period_end=False => immediate cancel (Stripe subscription deleted)

    Webhooks remain the source of truth, but we update local state immediately for UX.
    """
    _stripe_init()

    if not subscription.stripe_subscription_id:
        raise ValueError("Missing stripe_subscription_id on local subscription.")

    if at_period_end:
        # Schedule cancellation
        stripe_sub = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True,
        ).to_dict_recursive()

        subscription.cancel_at_period_end = True

        # Persist period end for UI messaging (best effort)
        cpe = _dt_from_unix(stripe_sub.get("current_period_end"))
        if cpe:
            subscription.current_period_end = cpe

        # Do NOT mark canceled yet; still active until period end
        subscription.save(
            update_fields=["cancel_at_period_end", "current_period_end", "updated_at"]
        )

    else:
        # Immediate cancel in Stripe (idempotent handling)
        try:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        except stripe.error.InvalidRequestError as e:
            msg = (getattr(e, "user_message", None) or str(e)).lower()
            if "no such subscription" not in msg:
                raise

        now = timezone.now()
        subscription.cancel_at_period_end = False
        subscription.status = "canceled"
        subscription.mrr_pennies = 0
        subscription.canceled_at = now
        subscription.ended_at = now
        subscription.current_period_end = now

        subscription.save(
            update_fields=[
                "cancel_at_period_end",
                "status",
                "mrr_pennies",
                "canceled_at",
                "ended_at",
                "current_period_end",
                "updated_at",
            ]
        )

    log_event(
        event_type="stripe_subscription_cancel_requested",
        entity_type="subscription",
        entity_id=subscription.id,
        user=user,
        metadata={
            "stripe_subscription_id": subscription.stripe_subscription_id,
            "at_period_end": at_period_end,
        },
    )
