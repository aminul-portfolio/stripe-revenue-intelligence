from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserRole
from orders.models import Order


class PaymentStartAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()

        self.cust_a = User.objects.create_user(username="cust_a", password="pass12345")
        UserRole.objects.update_or_create(
            user=self.cust_a, defaults={"role": "customer"}
        )

        self.cust_b = User.objects.create_user(username="cust_b", password="pass12345")
        UserRole.objects.update_or_create(
            user=self.cust_b, defaults={"role": "customer"}
        )

        self.order_a = Order.objects.create(
            user=self.cust_a,
            email="a@test.com",
            status="pending",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )

    def test_non_owner_gets_404_on_start_payment(self):
        ok = self.client.login(username="cust_b", password="pass12345")
        self.assertTrue(ok)

        try:
            url = reverse("start-payment", args=[self.order_a.id])
        except Exception:
            url = f"/payments/start/{self.order_a.id}/"

        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)
