from __future__ import annotations

import stripe
from django.conf import settings


def init_stripe() -> None:
    if not getattr(settings, "STRIPE_SECRET_KEY", ""):
        raise ValueError("STRIPE_SECRET_KEY is missing. Set it in .env / settings.")
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(
    *,
    amount_pennies: int,
    currency: str = "gbp",
    metadata: dict | None = None,
    idempotency_key: str | None = None,
):
    """
    Enterprise-grade PaymentIntent creation.

    - Validates amount and currency
    - Supports idempotency key to prevent duplicate PaymentIntents on retries
    """
    init_stripe()

    if not isinstance(amount_pennies, int):
        raise ValueError("amount_pennies must be an int.")
    if amount_pennies <= 0:
        raise ValueError("amount_pennies must be > 0.")

    currency = (currency or "gbp").lower().strip()
    if len(currency) != 3:
        raise ValueError("currency must be a 3-letter ISO code (e.g. 'gbp').")

    params = {
        "amount": amount_pennies,
        "currency": currency,
        "metadata": metadata or {},
        "automatic_payment_methods": {"enabled": True},
    }

    # Stripe "request options" (idempotency key belongs here)
    request_opts = {}
    if idempotency_key:
        request_opts["idempotency_key"] = idempotency_key

    if request_opts:
        return stripe.PaymentIntent.create(**params, **request_opts)

    return stripe.PaymentIntent.create(**params)
