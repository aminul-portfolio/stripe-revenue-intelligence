from django.utils import timezone
from audit.services.logger import log_event
from subscriptions.models import Subscription


def create_demo_subscription(user, product_name="Monthly Skincare Plan"):
    sub = Subscription.objects.create(
        user=user, product_name=product_name, status="active"
    )
    log_event(
        event_type="subscription_created",
        entity_type="subscription",
        entity_id=sub.id,
        user=user,
        metadata={"product": product_name},
    )
    return sub


def cancel_subscription(sub: Subscription, user=None):
    now = timezone.now()
    sub.status = "canceled"
    sub.canceled_at = now
    sub.save(update_fields=["status", "canceled_at"])

    log_event(
        event_type="subscription_canceled",
        entity_type="subscription",
        entity_id=sub.id,
        user=user,
        metadata={"canceled_at": now.isoformat()},
    )
