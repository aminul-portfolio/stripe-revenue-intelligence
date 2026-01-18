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
def reactivate_stripe_subscription(
    *, subscription: Subscription, user=None
) -> Subscription:
    """
    Reactivate a Stripe subscription that was scheduled to cancel at period end
    by setting cancel_at_period_end=False.

    Updates local row immediately for UX; webhooks remain source of truth.
    """
    _stripe_init()

    if not subscription.stripe_subscription_id:
        raise ValueError("Missing stripe_subscription_id on local subscription.")

    # Only makes sense if cancellation was scheduled
    if not subscription.cancel_at_period_end:
        return subscription

    try:
        stripe_sub = stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=False,
        ).to_dict_recursive()
    except stripe.error.InvalidRequestError as e:
        msg = (getattr(e, "user_message", None) or str(e)).lower()
        # If Stripe already deleted it, reactivation is impossible
        if "no such subscription" in msg:
            raise ValueError(
                "This subscription no longer exists in Stripe. Please create a new subscription."
            )
        raise

    subscription.cancel_at_period_end = bool(
        stripe_sub.get("cancel_at_period_end") or False
    )
    subscription.status = (
        stripe_sub.get("status") or subscription.status or "active"
    ).strip()

    subscription.current_period_end = _dt_from_unix(
        stripe_sub.get("current_period_end")
    )
    subscription.current_period_start = _dt_from_unix(
        stripe_sub.get("current_period_start")
    )

    # Reactivation means not canceled
    subscription.canceled_at = None
    subscription.ended_at = None

    subscription.save(
        update_fields=[
            "cancel_at_period_end",
            "status",
            "current_period_start",
            "current_period_end",
            "canceled_at",
            "ended_at",
            "updated_at",
        ]
    )

    log_event(
        event_type="stripe_subscription_reactivated",
        entity_type="subscription",
        entity_id=subscription.id,
        user=user,
        metadata={"stripe_subscription_id": subscription.stripe_subscription_id},
    )

    return subscription
