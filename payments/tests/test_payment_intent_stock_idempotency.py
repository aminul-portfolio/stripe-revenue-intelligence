from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from orders.models import Order, OrderItem
from products.models import Product, ProductVariant
from payments.services.webhook_handlers import (
    StockOversellError,
    handle_payment_intent_succeeded,
)


class PaymentIntentSucceededStockIdempotencyTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="u_stock",
            email="u_stock@example.com",
            password="pass12345",
        )

    def _make_order(self, *, total: Decimal = Decimal("10.00")) -> Order:
        return Order.objects.create(
            user=self.user,
            email=self.user.email,
            status="pending",
            subtotal=total,
            total=total,
        )

    def _intent_for_order(
        self, order: Order, *, intent_id: str = "pi_test_123"
    ) -> dict:
        # Important:
        # - Do NOT include amount_received => avoids optional amount mismatch check complexity.
        # - Provide latest_charge as a proper ch_ id so we exercise the preferred path.
        return {
            "id": intent_id,
            "metadata": {"order_id": str(order.id)},
            "latest_charge": "ch_test_123",
        }

    def test_product_stock_decrements_once_on_replay(self) -> None:
        """
        Proves idempotency at the handler boundary:
        - First call: order becomes paid and product stock decrements.
        - Second call (replay): no additional decrement.
        """
        product = Product.objects.create(
            name="P1",
            slug="p1",
            description="",
            price=Decimal("10.00"),
            is_active=True,
            stock=10,
            is_preorder=False,
        )

        order = self._make_order(total=Decimal("10.00"))
        OrderItem.objects.create(
            order=order,
            product=product,
            variant=None,
            product_name=product.name,
            sku="SKU-P1",
            unit_price=product.price,
            qty=2,
            line_total=Decimal("20.00"),
        )

        intent = self._intent_for_order(order, intent_id="pi_prod_1")

        handle_payment_intent_succeeded(intent=intent)

        order.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(product.stock, 8)

        # Replay (idempotent): must not decrement again
        handle_payment_intent_succeeded(intent=intent)

        order.refresh_from_db()
        product.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(product.stock, 8)

    def test_variant_stock_decrements_once_on_replay(self) -> None:
        """
        Variant path uses ProductVariant.stock with select_for_update.
        Replay must not double-decrement.
        """
        parent = Product.objects.create(
            name="P2",
            slug="p2",
            description="",
            price=Decimal("15.00"),
            is_active=True,
            stock=0,  # not used for variant path
            is_preorder=False,
        )
        variant = ProductVariant.objects.create(
            product=parent,
            name="Size L",
            sku="SKU-P2-L",
            price_override=None,
            stock=5,
        )

        order = self._make_order(total=Decimal("15.00"))
        OrderItem.objects.create(
            order=order,
            product=parent,  # ok to keep for analytics; handler uses variant_id branch first
            variant=variant,
            product_name=parent.name,
            sku=variant.sku,
            unit_price=variant.effective_price(),
            qty=3,
            line_total=Decimal("45.00"),
        )

        intent = self._intent_for_order(order, intent_id="pi_var_1")

        handle_payment_intent_succeeded(intent=intent)

        order.refresh_from_db()
        variant.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(variant.stock, 2)

        # Replay: must not decrement again
        handle_payment_intent_succeeded(intent=intent)

        order.refresh_from_db()
        variant.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(variant.stock, 2)

    def test_preorder_items_do_not_decrement_stock(self) -> None:
        """
        If product.is_preorder=True, handler should skip stock decrement.
        (Still marks the order as paid.)
        """
        preorder = Product.objects.create(
            name="P3",
            slug="p3",
            description="",
            price=Decimal("12.00"),
            is_active=True,
            stock=7,
            is_preorder=True,
        )

        order = self._make_order(total=Decimal("12.00"))
        OrderItem.objects.create(
            order=order,
            product=preorder,
            variant=None,
            product_name=preorder.name,
            sku="SKU-P3",
            unit_price=preorder.price,
            qty=4,
            line_total=Decimal("48.00"),
        )

        intent = self._intent_for_order(order, intent_id="pi_pre_1")

        handle_payment_intent_succeeded(intent=intent)

        order.refresh_from_db()
        preorder.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(preorder.stock, 7)  # unchanged

        # Replay remains unchanged
        handle_payment_intent_succeeded(intent=intent)

        preorder.refresh_from_db()
        self.assertEqual(preorder.stock, 7)

    def test_product_oversell_raises_and_does_not_decrement_below_zero(self) -> None:
        """
        Hardening: if qty > stock for non-preorder product, handler must raise
        and must not push stock negative.
        """
        product = Product.objects.create(
            name="P_OV1",
            slug="p-ov1",
            description="",
            price=Decimal("10.00"),
            is_active=True,
            stock=1,
            is_preorder=False,
        )

        order = self._make_order(total=Decimal("20.00"))
        OrderItem.objects.create(
            order=order,
            product=product,
            variant=None,
            product_name=product.name,
            sku="SKU-OV1",
            unit_price=product.price,
            qty=2,  # > stock
            line_total=Decimal("20.00"),
        )

        intent = self._intent_for_order(order, intent_id="pi_ov_prod_1")

        with self.assertRaises(StockOversellError):
            handle_payment_intent_succeeded(intent=intent)

        order.refresh_from_db()
        product.refresh_from_db()

        # Must not silently mark paid on oversell
        self.assertNotEqual(order.status, "paid")
        # Must not go negative
        self.assertEqual(product.stock, 1)

    def test_variant_oversell_raises_and_does_not_decrement_below_zero(self) -> None:
        """
        Hardening: if qty > stock for variant, handler must raise
        and must not push variant stock negative.
        """
        parent = Product.objects.create(
            name="P_OV2",
            slug="p-ov2",
            description="",
            price=Decimal("15.00"),
            is_active=True,
            stock=0,
            is_preorder=False,
        )
        variant = ProductVariant.objects.create(
            product=parent,
            name="Size XL",
            sku="SKU-OV2-XL",
            price_override=None,
            stock=1,
        )

        order = self._make_order(total=Decimal("30.00"))
        OrderItem.objects.create(
            order=order,
            product=parent,
            variant=variant,
            product_name=parent.name,
            sku=variant.sku,
            unit_price=variant.effective_price(),
            qty=2,  # > stock
            line_total=Decimal("30.00"),
        )

        intent = self._intent_for_order(order, intent_id="pi_ov_var_1")

        with self.assertRaises(StockOversellError):
            handle_payment_intent_succeeded(intent=intent)

        order.refresh_from_db()
        variant.refresh_from_db()

        self.assertNotEqual(order.status, "paid")
        self.assertEqual(variant.stock, 1)
