from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import timezone as dt_timezone
from typing import Optional

import stripe
from django.conf import settings
from django.db import transaction
from django.db.utils import OperationalError
from django.utils import timezone

from audit.services.logger import log_event
from subscriptions.models import Subscription


def _stripe_init() -> None:
    stripe.api_key = settings.STRIPE_SECRET_KEY


def _dt_from_unix(ts: Optional[int]):
    if not ts:
        return None
    return timezone.datetime.fromtimestamp(int(ts), tz=dt_timezone.utc)


def _sqlite_write_retry(fn, *, retries: int = 6, base_delay: float = 0.12):
    for i in range(retries):
        try:
            return fn()
        except OperationalError as e:
            if "database is locked" not in str(e).lower():
                raise
            time.sleep(base_delay * (i + 1))
    return fn()


def _extract_price_and_mrr(stripe_sub: dict) -> tuple[str, int]:
    """
    Returns (price_id, mrr_pennies). Assumes 1 line item.
    Requires expand=['items.data.price'] when retrieving subscription.
    """
    price_id = ""
    mrr_pennies = 0
    try:
        item0 = ((stripe_sub.get("items") or {}).get("data") or [])[0]
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


def _get_or_create_customer_id(*, user, stripe_customer_id: str = "") -> str:
    """
    Prefer passed-in customer id (session), else reuse from DB, else create.
    """
    _stripe_init()

    stripe_customer_id = (stripe_customer_id or "").strip()
    if stripe_customer_id:
        return stripe_customer_id

    existing = (
        Subscription.objects.filter(user=user)
        .exclude(stripe_customer_id="")
        .order_by("-id")
        .first()
    )
    if existing and existing.stripe_customer_id:
        return existing.stripe_customer_id

    cust = stripe.Customer.create(
        email=getattr(user, "email", "") or None,
        metadata={"user_id": str(user.id)},
    )
    return cust["id"]


def _ensure_customer_has_default_pm(*, stripe_customer_id: str) -> str:
    """
    Enforces 'Add Card first'. Returns default_payment_method id if present.
    """
    _stripe_init()
    cust = stripe.Customer.retrieve(stripe_customer_id).to_dict_recursive()
    invoice_settings = cust.get("invoice_settings") or {}
    default_pm = (invoice_settings.get("default_payment_method") or "").strip()

    if not default_pm:
        raise ValueError(
            "No default payment method found for this customer. "
            "Please add a card first (Subscriptions → Add Card)."
        )

    return default_pm


def _force_first_invoice_attempt_if_needed(
    *, stripe_sub: dict, default_pm: str
) -> None:
    _stripe_init()

    latest_invoice = stripe_sub.get("latest_invoice")
    inv_id = (
        latest_invoice
        if isinstance(latest_invoice, str)
        else (latest_invoice.get("id") if isinstance(latest_invoice, dict) else "")
    )
    inv_id = (inv_id or "").strip()
    if not inv_id:
        return

    inv = stripe.Invoice.retrieve(inv_id).to_dict_recursive()

    # If already paid/finalized, nothing to do
    if inv.get("paid") is True or inv.get("status") in ("paid", "void"):
        return

    # If draft, finalize it
    if inv.get("status") == "draft":
        inv = stripe.Invoice.finalize_invoice(inv_id).to_dict_recursive()

    # If still open and not paid, attempt to pay using default PM
    if inv.get("status") == "open" and not inv.get("paid"):
        try:
            stripe.Invoice.pay(inv_id, payment_method=default_pm)
        except Exception:
            pass


@dataclass(frozen=True)
class CreateSubscriptionResult:
    subscription: Subscription
    stripe_customer_id: str
    stripe_subscription_id: str


def create_stripe_subscription(
    *,
    user,
    price_id: str,
    product_name: str = "",
    stripe_customer_id: str = "",
) -> CreateSubscriptionResult:
    """
    Create a Stripe subscription that should go ACTIVE immediately.

    Requires:
    - Customer already has a default payment method (collected via SetupIntent flow).
    """
    _stripe_init()

    # 1) Choose correct customer id (session preferred)
    cust_id = _get_or_create_customer_id(
        user=user, stripe_customer_id=stripe_customer_id
    )

    # 2) Ensure card exists and capture default_pm (IMPORTANT)
    default_pm = _ensure_customer_has_default_pm(stripe_customer_id=cust_id)

    # 3) Create subscription
    stripe_sub = stripe.Subscription.create(
        customer=cust_id,
        items=[{"price": price_id}],
        collection_method="charge_automatically",
        payment_behavior="error_if_incomplete",
        payment_settings={
            # Save for future invoices; default_pm already exists on customer
            "save_default_payment_method": "on_subscription",
        },
        expand=["items.data.price", "latest_invoice"],
        metadata={"user_id": str(user.id)},
    )
    stripe_sub_dict = stripe_sub.to_dict_recursive()

    # Optional dev safeguard (NOW passes default_pm)
    _force_first_invoice_attempt_if_needed(
        stripe_sub=stripe_sub_dict, default_pm=default_pm
    )

    # Refresh to read updated status/periods
    stripe_sub_refreshed = stripe.Subscription.retrieve(
        stripe_sub_dict["id"],
        expand=["items.data.price"],
    ).to_dict_recursive()

    status = (stripe_sub_refreshed.get("status") or "incomplete").strip()
    cps = _dt_from_unix(stripe_sub_refreshed.get("current_period_start"))
    cpe = _dt_from_unix(stripe_sub_refreshed.get("current_period_end"))
    canceled_at = _dt_from_unix(stripe_sub_refreshed.get("canceled_at"))
    ended_at = _dt_from_unix(stripe_sub_refreshed.get("ended_at"))
    cancel_at_period_end = bool(
        stripe_sub_refreshed.get("cancel_at_period_end") or False
    )

    price_id_from_stripe, mrr_pennies = _extract_price_and_mrr(stripe_sub_refreshed)

    # 4) Write local row
    def _write():
        with transaction.atomic():
            return Subscription.objects.create(
                user=user,
                product_name=product_name,
                stripe_customer_id=cust_id,
                stripe_subscription_id=stripe_sub_refreshed["id"],
                stripe_price_id=price_id_from_stripe or price_id,
                status=status,
                current_period_start=cps,
                current_period_end=cpe,
                cancel_at_period_end=cancel_at_period_end,
                canceled_at=canceled_at,
                ended_at=ended_at,
                mrr_pennies=mrr_pennies,
            )

    local = _sqlite_write_retry(_write)

    log_event(
        event_type="stripe_subscription_created",
        entity_type="subscription",
        entity_id=local.id,
        user=user,
        metadata={
            "stripe_subscription_id": local.stripe_subscription_id,
            "stripe_customer_id": cust_id,
            "stripe_price_id": local.stripe_price_id,
            "status": local.status,
        },
    )

    return CreateSubscriptionResult(
        subscription=local,
        stripe_customer_id=cust_id,
        stripe_subscription_id=local.stripe_subscription_id,
    )
