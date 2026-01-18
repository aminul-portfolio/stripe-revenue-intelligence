from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from subscriptions.models import Subscription
from analyticsapp.services.subscriptions import subscription_kpis


class SubscriptionKpisTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="u1", email="u1@example.com", password="pass12345"
        )

    def test_subscription_kpis_uses_canceled_status_and_window_consistent_churn(self):
        """
        Regression: KPIs must use status='canceled' and churn must be
        calculated as (canceled_in_window / total_in_window) within the same window.
        """
        now = timezone.now()
        start = now - timedelta(days=30)
        end = now

        # In-window subscriptions
        Subscription.objects.create(user=self.user, product_name="P1", status="active")
        Subscription.objects.create(
            user=self.user, product_name="P2", status="canceled"
        )

        # Out-of-window subscription (must not affect window KPI counts)
        old_sub = Subscription.objects.create(
            user=self.user, product_name="P3", status="canceled"
        )
        Subscription.objects.filter(id=old_sub.id).update(
            created_at=now - timedelta(days=365)
        )

        kpis = subscription_kpis(start, end)

        self.assertEqual(kpis["total"], 2)
        self.assertEqual(kpis["active"], 1)
        self.assertEqual(kpis["canceled"], 1)
        self.assertEqual(kpis["churn"], 50.0)
