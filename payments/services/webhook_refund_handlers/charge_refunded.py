from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from audit.services.logger import log_event
from orders.models import Order


def handle_charge_refunded(*, charge: dict) -> None:
    """
    Stripe charge.refunded => update Order refund fields.

    Match order via:
      1) charge.metadata.order_id (preferred if present)
      2) Order.stripe_charge_id == charge.id (fallback)

    Updates:
      - refund_amount_pennies (from charge.amount_refunded)
      - refund_status: none/partial/full
      - refunded_at (when refund_amount_pennies > 0)

    Idempotent:
      - If we already recorded >= amount_refunded and status is partial/full, ignore.
    """
    charge_id = charge.get("id") or ""
    metadata = charge.get("metadata") or {}
    order_id = metadata.get("order_id")

    amount_refunded = int(charge.get("amount_refunded") or 0)
    amount_total = int(charge.get("amount") or 0)

    if not charge_id:
        log_event(
            event_type="stripe_refund_missing_charge_id",
            entity_type="charge",
            entity_id="unknown",
            metadata={"amount_refunded": amount_refunded},
        )
        return

    order = None
    if order_id:
        order = Order.objects.filter(id=order_id).first()

    if order is None:
        order = Order.objects.filter(stripe_charge_id=charge_id).first()

    if order is None:
        log_event(
            event_type="stripe_refund_order_not_found",
            entity_type="charge",
            entity_id=charge_id,
            metadata={"order_id": order_id, "amount_refunded": amount_refunded},
        )
        return

    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order.id)

        # Idempotency: ignore if we already recorded this refund amount (or more)
        if order.refund_amount_pennies >= amount_refunded and order.refund_status in (
            "partial",
            "full",
        ):
            log_event(
                event_type="stripe_refund_ignored_idempotent",
                entity_type="order",
                entity_id=order.id,
                metadata={"charge_id": charge_id, "amount_refunded": amount_refunded},
            )
            return

        order.refund_amount_pennies = amount_refunded

        if amount_total > 0 and amount_refunded >= amount_total:
            order.refund_status = "full"
        elif amount_refunded > 0:
            order.refund_status = "partial"
        else:
            order.refund_status = "none"

        if amount_refunded > 0:
            order.refunded_at = timezone.now()

        order.save(
            update_fields=["refund_amount_pennies", "refund_status", "refunded_at"]
        )

    log_event(
        event_type="order_refund_updated",
        entity_type="order",
        entity_id=order.id,
        metadata={
            "charge_id": charge_id,
            "refund_amount_pennies": amount_refunded,
            "charge_amount_pennies": amount_total,
            "refund_status": order.refund_status,
        },
    )
