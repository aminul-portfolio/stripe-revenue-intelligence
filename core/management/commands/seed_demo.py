from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

from products.models import Category, Product
from accounts.models import UserRole
from orders.models import Order, OrderItem


class Command(BaseCommand):
    help = "Seed demo data (products + roles)."

    def handle(self, *args, **options):
        cat, _ = Category.objects.get_or_create(name="Skincare", slug="skincare")
        demo_products = [
            ("Hydrating Eye Serum", 56.00, 20),
            ("Foaming Facial Cleanser", 85.00, 15),
            ("Daily Moisturiser", 49.00, 30),
            ("Gentle Toner", 32.00, 25),
            ("Vitamin C Serum", 65.00, 12),
            ("Night Repair Cream", 72.00, 10),
        ]
        for name, price, stock in demo_products:
            Product.objects.get_or_create(
                name=name,
                slug=slugify(name),
                defaults={
                    "category": cat,
                    "price": price,
                    "stock": stock,
                    "description": "Premium skincare product.",
                },
            )

        # Deterministic product picks for orders
        p1 = Product.objects.get(slug=slugify("Hydrating Eye Serum"))
        p2 = Product.objects.get(slug=slugify("Foaming Facial Cleanser"))

        User = get_user_model()
        admin_user, _ = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@example.com"}
        )
        admin_user.set_password("admin12345")
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        analyst, _ = User.objects.get_or_create(
            username="analyst", defaults={"email": "analyst@example.com"}
        )
        analyst.set_password("analyst12345")
        analyst.is_staff = True
        analyst.save()
        UserRole.objects.get_or_create(user=analyst, defaults={"role": "analyst"})

        ops, _ = User.objects.get_or_create(
            username="ops", defaults={"email": "ops@example.com"}
        )
        ops.set_password("ops12345")
        ops.is_staff = True
        ops.save()
        UserRole.objects.get_or_create(user=ops, defaults={"role": "ops"})

        # --- Orders realism (minimum interview/demo set) ---
        # Creates a small set of Orders spanning lifecycle + refund tracking.
        # Idempotent by email keys (so re-running seed_demo does not duplicate orders).

        def ensure_order(email: str, status: str, product: Product, qty: int = 1):
            order, _created = Order.objects.get_or_create(
                email=email,
                defaults={"status": status},
            )

            # Keep status consistent if order already exists
            fields_to_update = []
            if order.status != status:
                order.status = status
                fields_to_update.append("status")

            # If the order is paid/fulfilled in demo data, mark it as mock-paid to satisfy monitoring rules
            if status in {"paid", "fulfilled"}:
                if (order.stripe_payment_intent or "").strip() != "mock":
                    order.stripe_payment_intent = "mock"
                    fields_to_update.append("stripe_payment_intent")
                if (order.stripe_charge_id or "").strip() != "mock":
                    order.stripe_charge_id = "mock"
                    fields_to_update.append("stripe_charge_id")

            if fields_to_update:
                fields_to_update.append("updated_at")
                order.save(update_fields=fields_to_update)

            unit_price = product.price
            line_total = unit_price * qty

            # Ensure at least one item exists for this order
            OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={
                    "product_name": product.name,
                    "sku": "",
                    "unit_price": unit_price,
                    "qty": qty,
                    "line_total": line_total,
                },
            )

            # Compute totals deterministically from items
            subtotal = sum(i.line_total for i in order.items.all())
            order.subtotal = subtotal
            order.total = subtotal
            order.save(update_fields=["subtotal", "total", "updated_at"])
            return order

        # Lifecycle examples
        ensure_order("demo_pending@example.com", "pending", p1, qty=1)
        ensure_order("demo_paid@example.com", "paid", p1, qty=2)
        ensure_order("demo_fulfilled@example.com", "fulfilled", p2, qty=1)

        # Refund-tracked example (refund fields represent refunds; status remains 'paid')
        o_refunded = ensure_order("demo_refunded@example.com", "paid", p2, qty=1)
        o_refunded.refund_status = "full"
        o_refunded.refund_amount_pennies = int(o_refunded.total * 100)
        o_refunded.refunded_at = timezone.now()
        o_refunded.save(
            update_fields=[
                "refund_status",
                "refund_amount_pennies",
                "refunded_at",
                "updated_at",
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete. Users: admin/admin12345, analyst/analyst12345, ops/ops12345 | Orders: pending/paid/fulfilled/refund-tracked"
            )
        )
