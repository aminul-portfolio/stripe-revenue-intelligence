from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserRole
from orders.models import Order


class OpsOrderEndpointsTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.ops = User.objects.create_user(
            username="ops_staff",
            password="pass12345",
            is_staff=True,
        )
        UserRole.objects.update_or_create(user=self.ops, defaults={"role": "ops"})

        self.customer = User.objects.create_user(
            username="cust",
            password="pass12345",
            is_staff=False,
        )
        UserRole.objects.update_or_create(
            user=self.customer, defaults={"role": "customer"}
        )

        self.pending = Order.objects.create(
            email="a@test.com",
            status="pending",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )
        self.paid = Order.objects.create(
            email="b@test.com",
            status="paid",
            subtotal=Decimal("20.00"),
            total=Decimal("20.00"),
        )

    def test_customer_cannot_cancel(self):
        self.client.login(username="cust", password="pass12345")
        url = reverse("order-cancel", args=[self.pending.id])
        r = self.client.post(url)

        # staff_member_required usually redirects to admin login (302).
        # role_required may return 403 depending on your implementation.
        self.assertIn(r.status_code, (302, 403))

        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, "pending")

    def test_ops_can_cancel_pending(self):
        self.client.login(username="ops_staff", password="pass12345")
        url = reverse("order-cancel", args=[self.pending.id])
        r = self.client.post(url)

        self.assertEqual(r.status_code, 302)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, "cancelled")

    def test_ops_can_fulfill_paid(self):
        self.client.login(username="ops_staff", password="pass12345")
        url = reverse("order-fulfill", args=[self.paid.id])
        r = self.client.post(url)

        self.assertEqual(r.status_code, 302)
        self.paid.refresh_from_db()
        self.assertEqual(self.paid.status, "fulfilled")
