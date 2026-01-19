import stripe
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from orders.services.access import assert_can_access_order

from audit.services.logger import log_event
from orders.models import Order
from payments.services.webhook_router import process_stripe_event


def start_payment(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)

    # ✅ Security: prevent paying/viewing someone else's order
    assert_can_access_order(request, order)

    # ✅ Safety: prevent paying twice
    if order.status == "paid":
        messages.info(request, "This order is already paid.")
        return redirect("order-detail", order_id=order.id)

    # ✅ Safety: block invalid states
    if order.status in ("canceled", "fulfilled"):
        messages.error(request, f"Cannot pay an order that is {order.status}.")
        return redirect("order-detail", order_id=order.id)

    # ✅ Mock mode for local demo
    if not settings.PAYMENTS_USE_STRIPE:
        order.status = "paid"
        order.stripe_payment_intent = "mock"
        order.stripe_charge_id = "mock"
        order.save(
            update_fields=["status", "stripe_payment_intent", "stripe_charge_id"]
        )

        log_event(
            event_type="order_paid_mock",
            entity_type="order",
            entity_id=order.id,
            user=request.user if request.user.is_authenticated else None,
            metadata={"total": str(order.total)},
        )
        messages.success(request, "Payment completed (mock mode).")
        return redirect("order-detail", order_id=order.id)

    # ✅ Stripe mode: prevent generating multiple PaymentIntents (UX + safety)
    # ✅ Stripe mode: if a PaymentIntent already exists, reuse it (do not create a new one)
    if order.stripe_payment_intent and order.stripe_payment_intent.startswith("pi_"):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent)

        # If already succeeded, mark paid (optional safety) and redirect
        if intent.get("status") == "succeeded":
            order.status = "paid"
            order.stripe_charge_id = (
                intent.get("latest_charge") or order.stripe_charge_id
            )
            order.save(update_fields=["status", "stripe_charge_id"])
            messages.success(request, "Payment already completed.")
            return redirect("order-detail", order_id=order.id)

        # Otherwise render checkout again with the same client_secret
        return render(
            request,
            "payments/stripe_checkout.html",
            {
                "order": order,
                "client_secret": intent.get("client_secret"),
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            },
        )

    from payments.services.stripe_service import create_payment_intent

    amount_pennies = int(order.total * 100)

    # ✅ Idempotency key prevents duplicates on retries / refresh / network retry
    intent = create_payment_intent(
        amount_pennies=amount_pennies,
        metadata={"order_id": str(order.id)},
        idempotency_key=f"order:{order.id}:payment_intent",
    )

    order.stripe_payment_intent = intent["id"]
    order.save(update_fields=["stripe_payment_intent"])

    return render(
        request,
        "payments/stripe_checkout.html",
        {
            "order": order,
            "client_secret": intent["client_secret"],
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        },
    )


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook endpoint:
    - Verifies Stripe signature
    - Idempotently processes events (StripeEvent boundary)
    - Logs failures for observability
    """
    if not settings.PAYMENTS_USE_STRIPE:
        return HttpResponse(status=200)

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as exc:
        log_event(
            event_type="stripe_webhook_invalid_payload",
            entity_type="stripe",
            entity_id="unknown",
            metadata={"error": str(exc), "payload_len": len(payload)},
        )
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as exc:
        log_event(
            event_type="stripe_webhook_invalid_signature",
            entity_type="stripe",
            entity_id="unknown",
            metadata={"error": str(exc), "has_sig": bool(sig_header)},
        )
        return HttpResponse(status=400)

    log_event(
        event_type="stripe_webhook_received",
        entity_type="stripe",
        entity_id=event.get("id", "unknown"),
        metadata={"type": event.get("type")},
    )

    process_stripe_event(event=event)
    return HttpResponse(status=200)
