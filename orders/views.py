from __future__ import annotations

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from cart.services.cart import cart_summary
from .models import Order
from .services.access import assert_can_access_order
from .services.lifecycle import cancel_order, fulfill_order
from .services.order_creator import create_order_from_cart


def checkout(request):
    if request.method == "POST":
        email = (request.POST.get("email", "") or "").strip()
        if not email:
            messages.error(request, "Email is required.")
            return redirect("checkout")

        # Guard: do not allow checkout if cart is empty
        summary = cart_summary(request.session)
        if not summary.get("items"):
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        shipping = {
            "name": (request.POST.get("name", "") or "").strip(),
            "line1": (request.POST.get("line1", "") or "").strip(),
            "city": (request.POST.get("city", "") or "").strip(),
            "postcode": (request.POST.get("postcode", "") or "").strip(),
            "country": (request.POST.get("country", "GB") or "GB").strip()[:2].upper(),
        }

        try:
            order = create_order_from_cart(request, email=email, shipping=shipping)
        except ValidationError as e:
            # Expected business validation (stock/qty/product missing, etc.)
            messages.error(request, str(e))
            return redirect("cart")
        except Exception:
            # Safety: do not leak internal details in UI
            messages.error(
                request,
                "Could not create your order. Please review your cart and try again.",
            )
            return redirect("cart")

        # Guest/session allowlist to prevent order ID enumeration while still
        # allowing the same browser/session to view/pay the order.
        ids = request.session.get("order_access_ids", [])
        if order.id not in ids:
            ids.append(order.id)
        request.session["order_access_ids"] = ids
        request.session.modified = True

        return redirect("start-payment", order_id=order.id)

    # GET: if cart empty, redirect to cart (prevents dead checkout)
    summary = cart_summary(request.session)
    if not summary.get("items"):
        messages.info(request, "Your cart is empty.")
        return redirect("cart")

    return render(request, "orders/checkout.html", {"cart": summary})


def order_detail(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    assert_can_access_order(request, order)
    return render(request, "orders/order_detail.html", {"order": order})


@require_POST
@staff_member_required
@role_required("ops", "admin")
def order_cancel(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    reason = (request.POST.get("reason", "") or "").strip()

    try:
        updated = cancel_order(order=order, actor=request.user, reason=reason)
        messages.success(request, f"Order #{updated.id} cancelled.")
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect("order-detail", order_id=order.id)


@require_POST
@staff_member_required
@role_required("ops", "admin")
def order_fulfill(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    note = (request.POST.get("note", "") or "").strip()

    try:
        updated = fulfill_order(order=order, actor=request.user, note=note)
        messages.success(request, f"Order #{updated.id} fulfilled.")
    except ValidationError as e:
        messages.error(request, str(e))

    return redirect("order-detail", order_id=order.id)
