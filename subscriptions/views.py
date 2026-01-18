from __future__ import annotations

from typing import Optional

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from subscriptions.models import Subscription
from subscriptions.services.stripe_cancel import cancel_stripe_subscription
from subscriptions.services.stripe_reactivate import reactivate_stripe_subscription
from subscriptions.services.stripe_subscriptions import create_stripe_subscription


def _stripe_init() -> None:
    stripe.api_key = settings.STRIPE_SECRET_KEY


def _get_customer_id_for_user(request) -> str:
    """
    Best-effort customer id resolution:
    1) session
    2) DB (latest subscription row)
    """
    customer_id = (request.session.get("stripe_customer_id") or "").strip()
    if customer_id:
        return customer_id

    existing = (
        Subscription.objects.filter(user=request.user)
        .exclude(stripe_customer_id="")
        .order_by("-id")
        .first()
    )
    return (existing.stripe_customer_id or "").strip() if existing else ""


def _customer_has_default_pm(customer_id: str) -> bool:
    """
    Safe check: returns False on any Stripe/API error (never breaks the page).
    """
    if not customer_id:
        return False

    _stripe_init()
    try:
        cust = stripe.Customer.retrieve(customer_id).to_dict_recursive()
        inv = cust.get("invoice_settings") or {}
        default_pm = (inv.get("default_payment_method") or "").strip()
        return bool(default_pm)
    except Exception:
        return False


def _days_left(dt) -> Optional[int]:
    if not dt:
        return None
    delta = dt - timezone.now()
    return max(0, int(delta.total_seconds() // 86400))


@login_required
def my_subscriptions(request):
    subs = Subscription.objects.filter(user=request.user).order_by("-id")

    customer_id = _get_customer_id_for_user(request)
    if customer_id:
        request.session["stripe_customer_id"] = customer_id  # keep it sticky

    has_default_pm = _customer_has_default_pm(customer_id) if customer_id else False

    return render(
        request,
        "subscriptions/my_subscriptions.html",
        {"subs": subs, "has_default_pm": has_default_pm},
    )


@require_POST
@login_required
def create_subscription(request):
    """
    Create a Stripe subscription.
    Requires a saved default card first (SetupIntent flow).

    Resubscribe behavior:
    - If user has an active Stripe-backed subscription scheduled to cancel (cancel_at_period_end=True),
      treat this as "Reactivate" (remove scheduled cancel).
    - If user has an active Stripe-backed subscription not scheduled to cancel, block.
    - Ignore stale local-only rows where stripe_subscription_id is empty.
    """
    price_id = request.POST.get("price_id") or getattr(
        settings, "DEFAULT_STRIPE_PRICE_ID", ""
    )
    if not price_id:
        messages.error(
            request,
            "Missing Stripe price_id. Set DEFAULT_STRIPE_PRICE_ID in settings or pass price_id.",
        )
        return redirect("my-subscriptions")

    product_name = request.POST.get("product_name", "Subscription")

    # Reuse the same customer that you saved a card on (session/DB)
    stripe_customer_id = _get_customer_id_for_user(request)
    if stripe_customer_id:
        request.session["stripe_customer_id"] = stripe_customer_id

    # HARD GUARD: must have default card before creating/reactivating
    if not stripe_customer_id or not _customer_has_default_pm(stripe_customer_id):
        messages.error(request, "Please add a card first (Subscriptions → Add Card).")
        return redirect("my-subscriptions")

    # Stripe-backed active subscription (real)
    active_stripe = (
        Subscription.objects.filter(
            user=request.user,
            status="active",
            stripe_subscription_id__startswith="sub_",
        )
        .order_by("-id")
        .first()
    )

    # If active but scheduled to cancel => reactivate immediately (resubscribe)
    if active_stripe and active_stripe.cancel_at_period_end:
        try:
            reactivate_stripe_subscription(
                subscription=active_stripe, user=request.user
            )
            messages.success(
                request, "Subscription reactivated. Cancellation has been removed."
            )
        except Exception as exc:
            messages.error(request, f"Could not reactivate subscription: {exc}")
        return redirect("my-subscriptions")

    # If active and not scheduled to cancel => block (single active subscription policy)
    if active_stripe and not active_stripe.cancel_at_period_end:
        messages.info(request, "You already have an active subscription.")
        return redirect("my-subscriptions")

    # Otherwise create a new Stripe subscription
    try:
        try:
            create_stripe_subscription(
                user=request.user,
                price_id=price_id,
                product_name=product_name,
                stripe_customer_id=stripe_customer_id,
            )
        except TypeError:
            create_stripe_subscription(
                user=request.user,
                price_id=price_id,
                product_name=product_name,
            )

        messages.success(request, "Subscription created.")
        return redirect("my-subscriptions")

    except Exception as exc:
        messages.error(request, f"Subscription creation failed: {exc}")
        return redirect("my-subscriptions")


@require_POST
@login_required
def cancel(request, sub_id: int):
    sub = get_object_or_404(Subscription, id=sub_id, user=request.user)

    if sub.status == "canceled":
        messages.info(request, "This subscription is already canceled.")
        return redirect("my-subscriptions")

    try:
        # Schedule cancel at period end so user keeps access
        cancel_stripe_subscription(
            subscription=sub, user=request.user, at_period_end=True
        )

        # ✅ ADD THIS LINE HERE (refresh updated DB values)
        sub.refresh_from_db(fields=["current_period_end"])

        days = _days_left(sub.current_period_end)
        if days is None:
            messages.success(
                request,
                "Cancellation scheduled. You will keep access until the end of your billing period.",
            )
        else:
            messages.success(
                request,
                f"Cancellation scheduled. You will keep access for {days} more day(s).",
            )
    except Exception as exc:
        messages.error(request, f"Cancellation failed: {exc}")

    return redirect("my-subscriptions")


@require_POST
@login_required
def reactivate(request, sub_id: int):
    """
    Reactivate a cancel-scheduled subscription (cancel_at_period_end=False).
    """
    sub = get_object_or_404(Subscription, id=sub_id, user=request.user)

    try:
        reactivate_stripe_subscription(subscription=sub, user=request.user)
        messages.success(
            request, "Subscription reactivated. Cancellation has been removed."
        )
    except Exception as exc:
        messages.error(request, f"Reactivation failed: {exc}")

    return redirect("my-subscriptions")


@require_http_methods(["GET"])
@login_required
def add_payment_method(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    stripe_customer_id = _get_customer_id_for_user(request)

    if not stripe_customer_id:
        cust = stripe.Customer.create(
            email=getattr(request.user, "email", "") or None,
            metadata={"user_id": str(request.user.id)},
        )
        stripe_customer_id = cust["id"]

    request.session["stripe_customer_id"] = stripe_customer_id

    si = stripe.SetupIntent.create(
        customer=stripe_customer_id,
        payment_method_types=["card"],
        usage="off_session",
    )

    return render(
        request,
        "subscriptions/add_payment_method.html",
        {
            "stripe_pk": settings.STRIPE_PUBLISHABLE_KEY,
            "client_secret": si["client_secret"],
        },
    )


@require_http_methods(["GET"])
@login_required
def add_payment_method_complete(request):
    """
    Stripe redirects here with ?setup_intent=seti_... after confirmSetup.
    We retrieve SI, get pm_..., attach (if needed), and set as default.
    """
    _stripe_init()

    setup_intent_id = (request.GET.get("setup_intent") or "").strip()
    if not setup_intent_id.startswith("seti_"):
        messages.error(request, "Missing SetupIntent reference. Please try again.")
        return redirect("subscriptions-add-pm")

    stripe_customer_id = _get_customer_id_for_user(request)
    if not stripe_customer_id:
        messages.error(request, "Missing Stripe customer session. Please try again.")
        return redirect("subscriptions-add-pm")

    si = stripe.SetupIntent.retrieve(setup_intent_id).to_dict_recursive()
    pm = si.get("payment_method")

    pm_id = ""
    if isinstance(pm, str):
        pm_id = pm.strip()
    elif isinstance(pm, dict):
        pm_id = (pm.get("id") or "").strip()

    if not pm_id.startswith("pm_"):
        messages.error(
            request,
            "Setup succeeded but payment method was not returned. Please try again.",
        )
        return redirect("subscriptions-add-pm")

    # Attach (ignore “already attached”)
    try:
        stripe.PaymentMethod.attach(pm_id, customer=stripe_customer_id)
    except stripe.error.InvalidRequestError as e:
        msg = (getattr(e, "user_message", None) or str(e)).lower()
        if "already attached" not in msg and "has already been attached" not in msg:
            messages.error(
                request,
                f"Could not attach payment method: {getattr(e, 'user_message', str(e))}",
            )
            return redirect("subscriptions-add-pm")

    # Set default for invoices/subscriptions
    stripe.Customer.modify(
        stripe_customer_id,
        invoice_settings={"default_payment_method": pm_id},
    )

    messages.success(
        request, "Card saved successfully. You can now create a subscription."
    )
    return redirect("my-subscriptions")
