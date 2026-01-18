from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from accounts.models import UserRole
from orders.models import Order

User = get_user_model()


class OrderAccessTestCase(TestCase):
    ORDER_DETAIL_PATH_FMT = "/orders/{id}/"
    START_PAYMENT_PATH_FMT = "/payments/start/{id}/"

    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass")
        UserRole.objects.update_or_create(
            user=self.owner, defaults={"role": "customer"}
        )

        self.other = User.objects.create_user(username="other", password="pass")
        UserRole.objects.update_or_create(
            user=self.other, defaults={"role": "customer"}
        )

        self.ops = User.objects.create_user(
            username="ops_user", password="pass", is_staff=True
        )
        UserRole.objects.update_or_create(user=self.ops, defaults={"role": "ops"})

        self.order = Order.objects.create(
            user=self.owner,
            email="owner@test.com",
            status="pending",
            subtotal=Decimal("10.00"),
            total=Decimal("10.00"),
        )

    def test_owner_can_view_order_detail(self):
        self.client.login(username="owner", password="pass")
        r = self.client.get(self.ORDER_DETAIL_PATH_FMT.format(id=self.order.id))
        self.assertEqual(r.status_code, 200)

    def test_other_customer_cannot_view_order_detail(self):
        self.client.login(username="other", password="pass")
        r = self.client.get(self.ORDER_DETAIL_PATH_FMT.format(id=self.order.id))
        self.assertEqual(r.status_code, 404)

    def test_ops_can_view_any_order_detail(self):
        self.client.login(username="ops_user", password="pass")
        r = self.client.get(self.ORDER_DETAIL_PATH_FMT.format(id=self.order.id))
        self.assertEqual(r.status_code, 200)

    @override_settings(PAYMENTS_USE_STRIPE=False)
    def test_start_payment_enforces_access(self):
        self.client.login(username="other", password="pass")
        r = self.client.get(self.START_PAYMENT_PATH_FMT.format(id=self.order.id))
        self.assertEqual(r.status_code, 404)

        self.client.login(username="owner", password="pass")
        r = self.client.get(self.START_PAYMENT_PATH_FMT.format(id=self.order.id))
        self.assertEqual(r.status_code, 302)
