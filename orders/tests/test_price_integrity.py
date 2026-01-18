from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import AnonymousUser

from cart.services.cart import add_to_cart, CART_SESSION_KEY
from orders.services.order_creator import create_order_from_cart
from products.models import Category, Product, ProductVariant


def _add_session_to_request(request):
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    return request


class CheckoutPriceIntegrityTests(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.category = Category.objects.create(name="Cat", slug="cat")

    def test_checkout_uses_db_price_not_session_price(self):
        product = Product.objects.create(
            name="P1",
            slug="p1",
            category=self.category,
            price=Decimal("72.00"),
            stock=10,
            is_active=True,
            is_preorder=False,
        )

        request = _add_session_to_request(self.rf.get("/"))
        request.user = AnonymousUser()

        # Add legit cart line
        add_to_cart(request.session, product_id=product.id, qty=1, variant_id=None)

        # Tamper session: inject fake price fields (must be ignored by order_creator)
        cart = request.session.get(CART_SESSION_KEY, {})
        key = f"{product.id}:"
        cart[key]["price"] = "0.01"
        cart[key]["line_total"] = "0.01"
        request.session[CART_SESSION_KEY] = cart
        request.session.save()

        order = create_order_from_cart(
            request,
            email="a@test.com",
            shipping={
                "name": "A",
                "line1": "L1",
                "city": "C",
                "postcode": "P",
                "country": "GB",
            },
        )

        self.assertEqual(order.subtotal, Decimal("72.00"))
        self.assertEqual(order.total, Decimal("72.00"))
        self.assertEqual(order.items.count(), 1)

        item = order.items.first()
        self.assertEqual(item.unit_price, Decimal("72.00"))
        self.assertEqual(item.qty, 1)
        self.assertEqual(item.line_total, Decimal("72.00"))

    def test_variant_price_override_used(self):
        product = Product.objects.create(
            name="P2",
            slug="p2",
            category=self.category,
            price=Decimal("100.00"),
            stock=10,
            is_active=True,
            is_preorder=False,
        )
        variant = ProductVariant.objects.create(
            product=product,
            name="V1",
            sku="SKU-V1",
            price_override=Decimal("80.00"),
            stock=10,
        )

        request = _add_session_to_request(self.rf.get("/"))
        request.user = AnonymousUser()

        add_to_cart(
            request.session, product_id=product.id, qty=2, variant_id=variant.id
        )

        order = create_order_from_cart(
            request,
            email="b@test.com",
            shipping={
                "name": "B",
                "line1": "L1",
                "city": "C",
                "postcode": "P",
                "country": "GB",
            },
        )

        self.assertEqual(order.total, Decimal("160.00"))
        item = order.items.first()
        self.assertEqual(item.unit_price, Decimal("80.00"))
        self.assertEqual(item.qty, 2)
        self.assertEqual(item.line_total, Decimal("160.00"))
        self.assertEqual(item.sku, "SKU-V1")

    def test_stock_blocked_when_not_preorder(self):
        product = Product.objects.create(
            name="P3",
            slug="p3",
            category=self.category,
            price=Decimal("10.00"),
            stock=1,
            is_active=True,
            is_preorder=False,
        )

        request = _add_session_to_request(self.rf.get("/"))
        request.user = AnonymousUser()

        # Stock enforcement happens at cart level now
        with self.assertRaises(ValidationError):
            add_to_cart(request.session, product_id=product.id, qty=2, variant_id=None)

    def test_stock_not_blocked_when_preorder(self):
        product = Product.objects.create(
            name="P4",
            slug="p4",
            category=self.category,
            price=Decimal("12.00"),
            stock=0,
            is_active=True,
            is_preorder=True,  # preorder bypasses stock check
        )

        request = _add_session_to_request(self.rf.get("/"))
        request.user = AnonymousUser()

        add_to_cart(request.session, product_id=product.id, qty=3, variant_id=None)

        order = create_order_from_cart(
            request,
            email="d@test.com",
            shipping={
                "name": "D",
                "line1": "L1",
                "city": "C",
                "postcode": "P",
                "country": "GB",
            },
        )

        self.assertEqual(order.total, Decimal("36.00"))
        self.assertEqual(order.items.count(), 1)
