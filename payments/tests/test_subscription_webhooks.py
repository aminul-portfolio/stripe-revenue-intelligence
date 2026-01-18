from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

from django.contrib.auth import get_user_model
from django.test import TestCase

from subscriptions.models import Subscription

from payments.services.webhook_subscription_handlers.subscription_deleted import (
    handle_customer_subscription_deleted,
)
from payments.services.webhook_subscription_handlers.subscription_updated import (
    handle_customer_subscription_updated,
)


def _ts(dt: datetime) -> int:
    # Stripe unix timestamps are integers (seconds)
    return int(dt.timestamp())


class SubscriptionWebhookHandlerTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="u1",
            email="u1@example.com",
            password="pass12345",
        )

        self.local = Subscription.objects.create(
            user=self.user,
            product_name="Pro Plan",
            stripe_customer_id="cus_test_123",
            stripe_subscription_id="sub_test_123",
            stripe_price_id="price_old",
            status="active",
            cancel_at_period_end=False,
            current_period_start=None,
            current_period_end=None,
            canceled_at=None,  # keep None because it's active
            ended_at=None,
            mrr_pennies=999,
        )

    def test_subscription_updated_syncs_fields_including_cancel_at_period_end(
        self,
    ) -> None:
        cps = datetime(2026, 1, 1, 0, 0, 0, tzinfo=dt_timezone.utc)
        cpe = datetime(2026, 2, 1, 0, 0, 0, tzinfo=dt_timezone.utc)

        payload = {
            "id": "sub_test_123",
            "status": "active",
            "cancel_at_period_end": True,
            "current_period_start": _ts(cps),
            "current_period_end": _ts(cpe),
            "canceled_at": None,
            "ended_at": None,
            "items": {
                "data": [
                    {
                        "price": {
                            "id": "price_new",
                            "unit_amount": 1200,  # pennies
                            "recurring": {"interval": "month", "interval_count": 1},
                        }
                    }
                ]
            },
        }

        handle_customer_subscription_updated(subscription=payload)

        self.local.refresh_from_db()
        self.assertEqual(self.local.status, "active")
        self.assertTrue(self.local.cancel_at_period_end)
        self.assertEqual(self.local.current_period_start, cps)
        self.assertEqual(self.local.current_period_end, cpe)
        self.assertEqual(self.local.stripe_price_id, "price_new")
        self.assertEqual(self.local.mrr_pennies, 1200)

    def test_subscription_deleted_sets_canceled_status_and_timestamps_and_zero_mrr(
        self,
    ) -> None:
        ended = datetime(2026, 1, 16, 14, 21, 55, tzinfo=dt_timezone.utc)

        payload = {
            "id": "sub_test_123",
            "ended_at": _ts(ended),
            "canceled_at": _ts(ended),
        }

        handle_customer_subscription_deleted(subscription=payload)

        self.local.refresh_from_db()
        self.assertEqual(self.local.status, "canceled")
        self.assertFalse(self.local.cancel_at_period_end)
        self.assertEqual(self.local.ended_at, ended)
        self.assertEqual(self.local.canceled_at, ended)
        self.assertEqual(self.local.mrr_pennies, 0)

    def test_updated_ignores_unknown_subscription_id(self) -> None:
        payload = {"id": "sub_does_not_exist", "status": "active"}
        handle_customer_subscription_updated(subscription=payload)

        # No crash; existing row unchanged
        self.local.refresh_from_db()
        self.assertEqual(self.local.stripe_subscription_id, "sub_test_123")
        self.assertEqual(self.local.status, "active")
