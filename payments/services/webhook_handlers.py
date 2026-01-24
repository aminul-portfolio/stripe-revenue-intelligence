from __future__ import annotations

from decimal import Decimal
from typing import Any, Tuple

from django.db import transaction

from audit.services.logger import log_event
from orders.models import Order
from products.models import Product, ProductVariant


class StockOversellError(ValueError):
    """Raised when an order attempts to consume more stock than is available."""


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _expected_amount_pennies(order: Order) -> int:
    # Avoid float conversion issues
    # order.total is Decimal (expected)
    total = Decimal(str(order.total or "0"))
    return int(total * 100)


def _extract_charge_or_payment_ref(intent: dict) -> Tuple[str, str]:
    """
    Returns (charge_id, payment_ref)

    - charge_id: preferred canonical Stripe Charge id (usually 'ch_...')
    - payment_ref: fallback reference (whatever Stripe gave us) if not 'ch_...'

    This avoids breaking when Stripe returns a non-'ch_' reference in latest_charge.
    """
    raw = intent.get("latest_charge")

    # If expanded object comes through
    if isinstance(raw, dict):
        raw_id = (raw.get("id") or "").strip()
    else:
        raw_id = (str(raw) if raw else "").strip()

    charge_id = ""
    payment_ref = ""

    if raw_id.startswith("ch_"):
        charge_id = raw_id
    elif raw_id:
        payment_ref = raw_id

    # If we still don't have a charge_id, try charges list (sometimes present/expanded)
    charges = (intent.get("charges") or {}).get("data") or []
    for ch in charges:
        ch_id = (ch.get("id") or "").strip()
        if ch_id.startswith("ch_"):
            charge_id = ch_id
            break

    return charge_id, payment_ref


def handle_payment_intent_succeeded(*, intent: dict) -> None:
    """
    PaymentIntent succeeded => mark order paid and decrement stock safely.

    Idempotency:
    - Lock order row (select_for_update)
    - If already paid, exit safely (no double stock decrement)

    Integrity:
    - Optional amount_received check (pennies)
    - Prevent negative stock (raise to force visibility)

    Stripe refs:
    - Persist PaymentIntent id
    - Persist best available charge/payment reference
    - Log if Stripe gave a non-'ch_' reference
    """
    metadata = intent.get("metadata") or {}
    order_id_raw = metadata.get("order_id")

    intent_id = (intent.get("id") or "").strip()

    if not order_id_raw:
        log_event(
            event_type="stripe_intent_missing_order_id",
            entity_type="payment_intent",
            entity_id=intent_id or "unknown",
            metadata={"reason": "metadata.order_id missing"},
        )
        return

    order_id = _to_int(order_id_raw, default=0)
    if order_id <= 0:
        log_event(
            event_type="stripe_intent_bad_order_id",
            entity_type="payment_intent",
            entity_id=intent_id or "unknown",
            metadata={"order_id": str(order_id_raw)},
        )
        return

    charge_id, payment_ref = _extract_charge_or_payment_ref(intent)

    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(id=order_id)
        except Order.DoesNotExist:
            log_event(
                event_type="stripe_order_not_found",
                entity_type="order",
                entity_id=str(order_id),
                metadata={"payment_intent": intent_id},
            )
            return

        # Idempotency: already paid => do nothing
        if order.status == "paid":
            return

        # Block invalid transitions
        if order.status in ("canceled", "fulfilled"):
            log_event(
                event_type="stripe_payment_for_invalid_order_state",
                entity_type="order",
                entity_id=order.id,
                user=order.user,
                metadata={"status": order.status, "payment_intent": intent_id},
            )
            return

        # Amount integrity check (optional but recommended)
        amount_received = intent.get("amount_received")
        if amount_received is not None:
            expected = _expected_amount_pennies(order)
            received = _to_int(amount_received, default=-1)
            if received != expected:
                log_event(
                    event_type="stripe_amount_mismatch",
                    entity_type="order",
                    entity_id=order.id,
                    user=order.user,
                    metadata={
                        "expected_pennies": expected,
                        "received_pennies": received,
                        "payment_intent": intent_id,
                    },
                )
                raise ValueError("Payment amount mismatch detected.")

        # Mark as paid first (still inside transaction)
        order.status = "paid"

        if intent_id:
            order.stripe_payment_intent = intent_id

        # Store the best reference we have (prefer charge_id)
        if charge_id:
            order.stripe_charge_id = charge_id
        elif payment_ref:
            # Keep using the same field for now to avoid migrations
            order.stripe_charge_id = payment_ref
            log_event(
                event_type="stripe_non_charge_payment_ref",
                entity_type="order",
                entity_id=order.id,
                user=order.user,
                metadata={"payment_intent": intent_id, "ref": payment_ref},
            )

        order.save(
            update_fields=["status", "stripe_payment_intent", "stripe_charge_id"]
        )

        # Decrement stock (atomic & locked)
        items = order.items.all().select_related("product", "variant")

        for item in items:
            qty = int(item.qty or 0)
            if qty <= 0:
                log_event(
                    event_type="order_item_invalid_qty",
                    entity_type="order_item",
                    entity_id=item.id,
                    metadata={"order_id": order.id, "qty": item.qty},
                )
                continue

            # Variant path
            if getattr(item, "variant_id", None):
                variant = ProductVariant.objects.select_for_update().get(
                    id=item.variant_id
                )
                product = Product.objects.select_for_update().get(id=variant.product_id)

                if product.is_preorder:
                    continue

                if variant.stock < qty:
                    log_event(
                        event_type="stock_negative_prevented",
                        entity_type="variant",
                        entity_id=variant.id,
                        metadata={
                            "order_id": order.id,
                            "requested": qty,
                            "available": variant.stock,
                            "sku": variant.sku,
                        },
                    )
                    raise StockOversellError(
                        f"Variant oversell prevented: variant_id={variant.id} sku={variant.sku} "
                        f"available={variant.stock} requested={qty} order_id={order.id}"
                    )

                variant.stock -= qty
                variant.save(update_fields=["stock"])
                continue

            # Product path
            if getattr(item, "product_id", None):
                product = Product.objects.select_for_update().get(id=item.product_id)

                if product.is_preorder:
                    continue

                if product.stock < qty:
                    log_event(
                        event_type="stock_negative_prevented",
                        entity_type="product",
                        entity_id=product.id,
                        metadata={
                            "order_id": order.id,
                            "requested": qty,
                            "available": product.stock,
                            "product": product.name,
                        },
                    )
                    raise StockOversellError(
                        f"Product oversell prevented: product_id={product.id} name={product.name} "
                        f"available={product.stock} requested={qty} order_id={order.id}"
                    )

                product.stock -= qty
                product.save(update_fields=["stock"])
                continue

            # Legacy compatibility
            log_event(
                event_type="order_item_missing_refs",
                entity_type="order_item",
                entity_id=item.id,
                metadata={
                    "order_id": order.id,
                    "sku": getattr(item, "sku", ""),
                    "product_name": getattr(item, "product_name", ""),
                },
            )

        log_event(
            event_type="order_paid_stripe",
            entity_type="order",
            entity_id=order.id,
            user=order.user,
            metadata={
                "total": str(order.total),
                "payment_intent": intent_id,
                "charge_id": charge_id or "",
                "payment_ref": payment_ref or "",
            },
        )


def handle_payment_intent_failed(*, intent: dict) -> None:
    metadata = intent.get("metadata") or {}
    order_id = metadata.get("order_id")
    intent_id = (intent.get("id") or "unknown").strip()

    log_event(
        event_type="payment_intent_failed",
        entity_type="payment_intent",
        entity_id=intent_id,
        metadata={"order_id": order_id},
    )


def handle_charge_refunded(*, charge: dict) -> None:
    charge_id = (charge.get("id") or "unknown").strip()
    payment_intent = (charge.get("payment_intent") or "").strip()

    log_event(
        event_type="charge_refunded",
        entity_type="charge",
        entity_id=charge_id,
        metadata={"payment_intent": payment_intent},
    )
