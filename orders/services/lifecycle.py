from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from audit.services.logger import log_event
from orders.models import Order


def cancel_order(*, order: Order, actor, reason: str = "") -> Order:
    """
    Allowed transition:
      pending -> cancelled

    Not allowed:
      paid/fulfilled/cancelled -> cancelled

    Notes:
    - We do NOT restock here because stock decrement happens on payment success.
    - This is a pure lifecycle transition + audit log.
    """
    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)

        # Idempotency: cancel is safe to retry
        if locked.status == "cancelled":
            return locked

        if locked.status != "pending":
            raise ValidationError(
                f"Only pending orders can be cancelled (current: {locked.status})."
            )

        locked.status = "cancelled"
        locked.save(update_fields=["status"])

    log_event(
        event_type="order_cancelled",
        entity_type="order",
        entity_id=locked.id,
        user=actor if getattr(actor, "is_authenticated", False) else None,
        metadata={"reason": reason or ""},
    )
    return locked


def fulfill_order(*, order: Order, actor, note: str = "") -> Order:
    """
    Allowed transition:
      paid -> fulfilled

    Not allowed:
      pending/cancelled/fulfilled -> fulfilled
    """
    with transaction.atomic():
        locked = Order.objects.select_for_update().get(pk=order.pk)

        # Idempotency: fulfill is safe to retry
        if locked.status == "fulfilled":
            return locked

        if locked.status != "paid":
            raise ValidationError(
                f"Only paid orders can be fulfilled (current: {locked.status})."
            )

        locked.status = "fulfilled"
        locked.save(update_fields=["status"])

    log_event(
        event_type="order_fulfilled",
        entity_type="order",
        entity_id=locked.id,
        user=actor if getattr(actor, "is_authenticated", False) else None,
        metadata={"note": note or ""},
    )
    return locked
