from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from subscriptions.models import Subscription


class SubscriptionStatusGuardTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="status-guard-user",
            email="status-guard@example.com",
            password="pass12345",
        )

    def test_rejects_invalid_status_string_cancelled(self) -> None:
        with self.assertRaises(IntegrityError):
            Subscription.objects.create(
                user=self.user,
                product_name="P1",
                status="cancelled",  # invalid; canonical is "canceled"
            )
