from __future__ import annotations

import threading
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connections
from django.test import TransactionTestCase

from orders.models import Order, OrderItem
from products.models import Product

from payments.services.webhook_handlers import (
    StockOversellError,
    handle_payment_intent_succeeded,
)


class StockConcurrencyHardeningTests(TransactionTestCase):
    """
    Proves stock decrement is safe under contention.

    Why TransactionTestCase:
    - Django TestCase wraps each test in a transaction, which can hide lock behavior.
    - TransactionTestCase allows separate real transactions and thread contention.
    """

    reset_sequences = True

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="u_conc",
            email="u_conc@example.com",
            password="pass12345",
        )

    def _make_order(self, *, total: Decimal) -> Order:
        return Order.objects.create(
            user=self.user,
            email=self.user.email,
            status="pending",
            subtotal=total,
            total=total,
        )

    def _intent_for_order(self, order: Order, *, intent_id: str) -> dict:
        return {
            "id": intent_id,
            "metadata": {"order_id": str(order.id)},
            "latest_charge": "ch_test_123",
        }

    def _runner(self, intent: dict, results: list[str], idx: int) -> None:
        """
        Each thread uses its own DB connection to simulate real concurrency.
        """
        connections.close_all()
        try:
            handle_payment_intent_succeeded(intent=intent)
            results[idx] = "ok"
        except StockOversellError:
            results[idx] = "oversell"
        except Exception as e:
            results[idx] = f"error:{type(e).__name__}"

    def test_two_orders_compete_for_one_stock_only_one_succeeds(self) -> None:
        """
        Setup:
        - Product stock = 1
        - Two different orders each try to buy qty=1 of the same product
        Expect:
        - Exactly one order becomes paid
        - The other fails with StockOversellError (or is not paid)
        - Final stock = 0 (never negative)
        """
        product = Product.objects.create(
            name="P_CONC",
            slug="p-conc",
            description="",
            price=Decimal("10.00"),
            is_active=True,
            stock=1,
            is_preorder=False,
        )

        order1 = self._make_order(total=Decimal("10.00"))
        OrderItem.objects.create(
            order=order1,
            product=product,
            variant=None,
            product_name=product.name,
            sku="SKU-CONC-1",
            unit_price=product.price,
            qty=1,
            line_total=Decimal("10.00"),
        )

        order2 = self._make_order(total=Decimal("10.00"))
        OrderItem.objects.create(
            order=order2,
            product=product,
            variant=None,
            product_name=product.name,
            sku="SKU-CONC-2",
            unit_price=product.price,
            qty=1,
            line_total=Decimal("10.00"),
        )

        intent1 = self._intent_for_order(order1, intent_id="pi_conc_1")
        intent2 = self._intent_for_order(order2, intent_id="pi_conc_2")

        results = ["", ""]

        t1 = threading.Thread(target=self._runner, args=(intent1, results, 0))
        t2 = threading.Thread(target=self._runner, args=(intent2, results, 1))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        order1.refresh_from_db()
        order2.refresh_from_db()
        product.refresh_from_db()

        paid_count = sum(1 for o in (order1, order2) if o.status == "paid")
        self.assertEqual(paid_count, 1, msg=f"results={results}")

        self.assertEqual(product.stock, 0, msg=f"results={results}")
        self.assertGreaterEqual(product.stock, 0, msg=f"results={results}")
