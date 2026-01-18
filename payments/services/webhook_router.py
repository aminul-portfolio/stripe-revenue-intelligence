from __future__ import annotations

import time

from django.db import connection, transaction
from django.db.utils import OperationalError
from django.utils import timezone

from audit.services.logger import log_event
from payments.models import StripeEvent

from .webhook_handlers import (
    handle_payment_intent_failed,
    handle_payment_intent_succeeded,
)
from .webhook_refund_handlers.charge_refunded import handle_charge_refunded

from .webhook_subscription_handlers.invoice_paid import handle_invoice_paid
from .webhook_subscription_handlers.invoice_payment_failed import (
    handle_invoice_payment_failed,
)
from .webhook_subscription_handlers.subscription_deleted import (
    handle_customer_subscription_deleted,
)
from .webhook_subscription_handlers.subscription_updated import (
    handle_customer_subscription_updated,
)


SUPPORTED_EVENT_TYPES = {
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "charge.refunded",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.paid",
    "invoice.payment_failed",
}


def _sqlite_retry(fn, *, retries: int = 6, base_delay: float = 0.12):
    """
    SQLite allows a single writer. Under Stripe webhook bursts + user requests,
    concurrent writes can raise 'database is locked'. This retry smooths it out in dev.
    """
    for i in range(retries):
        try:
            return fn()
        except OperationalError as e:
            if "database is locked" not in str(e).lower():
                raise
            time.sleep(base_delay * (i + 1))
    return fn()  # last attempt, let it raise if still locked


def process_stripe_event(*, event: dict) -> None:
    event_id = event.get("id")
    event_type = event.get("type")
    data_object = (event.get("data") or {}).get("object") or {}

    if not event_id or not event_type:
        return

    # Ignore noise events BEFORE touching DB
    if event_type not in SUPPORTED_EVENT_TYPES:
        return

    def _do():
        with transaction.atomic():
            stripe_event, _created = StripeEvent.objects.get_or_create(
                event_id=event_id,
                defaults={
                    "event_type": event_type,
                    "payload": event,
                    "status": "received",
                },
            )

            # Avoid select_for_update on SQLite (no real row locks; increases contention)
            if connection.features.has_select_for_update:
                stripe_event = StripeEvent.objects.select_for_update().get(
                    pk=stripe_event.pk
                )
            else:
                stripe_event = StripeEvent.objects.get(pk=stripe_event.pk)

            if stripe_event.status == "processed":
                return

            try:
                if event_type == "payment_intent.succeeded":
                    handle_payment_intent_succeeded(intent=data_object)

                elif event_type == "payment_intent.payment_failed":
                    handle_payment_intent_failed(intent=data_object)

                elif event_type == "charge.refunded":
                    handle_charge_refunded(charge=data_object)

                elif event_type in (
                    "customer.subscription.created",
                    "customer.subscription.updated",
                ):
                    handle_customer_subscription_updated(subscription=data_object)

                elif event_type == "customer.subscription.deleted":
                    handle_customer_subscription_deleted(subscription=data_object)

                elif event_type == "invoice.paid":
                    handle_invoice_paid(invoice=data_object)

                elif event_type == "invoice.payment_failed":
                    handle_invoice_payment_failed(invoice=data_object)

                # Mark processed
                stripe_event.status = "processed"
                stripe_event.processed_at = timezone.now()
                stripe_event.save(update_fields=["status", "processed_at"])

                log_event(
                    event_type="stripe_event_processed",
                    entity_type="stripe",
                    entity_id=event_id,
                    metadata={"type": event_type},
                )

            except Exception as exc:
                stripe_event.status = "failed"
                stripe_event.processed_at = timezone.now()
                stripe_event.save(update_fields=["status", "processed_at"])

                log_event(
                    event_type="stripe_event_failed",
                    entity_type="stripe",
                    entity_id=event_id,
                    metadata={"type": event_type, "error": str(exc)},
                )
                raise

    # Retry only helps on SQLite/dev; harmless elsewhere
    _sqlite_retry(_do)
