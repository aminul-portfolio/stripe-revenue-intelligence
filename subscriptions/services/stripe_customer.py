from __future__ import annotations

import stripe
from django.conf import settings

from subscriptions.models import StripeCustomer


def _stripe_init() -> None:
    stripe.api_key = settings.STRIPE_SECRET_KEY


def get_or_create_stripe_customer_id(*, user) -> str:
    """
    Single source of truth for stripe customer id.
    """
    _stripe_init()

    obj = StripeCustomer.objects.filter(user=user).first()
    if obj:
        return obj.stripe_customer_id

    cust = stripe.Customer.create(
        email=getattr(user, "email", "") or None,
        metadata={"user_id": str(user.id)},
    )
    return StripeCustomer.objects.create(
        user=user, stripe_customer_id=cust["id"]
    ).stripe_customer_id


def customer_has_default_pm(*, customer_id: str) -> bool:
    if not customer_id:
        return False
    _stripe_init()
    c = stripe.Customer.retrieve(customer_id).to_dict_recursive()
    default_pm = (
        (c.get("invoice_settings") or {}).get("default_payment_method") or ""
    ).strip()
    return bool(default_pm)
