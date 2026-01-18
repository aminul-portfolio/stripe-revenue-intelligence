from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from cart.services.cart import cart_summary, clear
from audit.services.logger import log_event

from products.models import Product, ProductVariant
from orders.models import Order, OrderItem


def _get_effective_price(product: Product, variant: ProductVariant | None) -> Decimal:
    if variant and variant.price_override is not None:
        return variant.price_override
    return product.price


def create_order_from_cart(request, *, email: str, shipping: dict):
    cart = cart_summary(request.session)
    if not cart["items"]:
        raise ValidationError("Cart is empty.")

    # Optional: max per line item safety limit
    MAX_QTY_PER_ITEM = 50

    with transaction.atomic():
        # We will build validated items from DB (single source of truth)
        validated_items = []
        subtotal = Decimal("0.00")

        for row in cart["items"]:
            # ---- Extract identity safely ----
            # Your cart rows may carry objects; we prefer IDs.
            product_obj = row.get("product")
            variant_obj = row.get("variant")

            product_id = getattr(product_obj, "id", None) or row.get("product_id")
            variant_id = getattr(variant_obj, "id", None) or row.get("variant_id")

            qty = int(row.get("qty") or 0)
            if qty < 1:
                raise ValidationError("Invalid quantity (must be at least 1).")
            if qty > MAX_QTY_PER_ITEM:
                raise ValidationError(f"Quantity too large (max {MAX_QTY_PER_ITEM}).")

            # ---- Lock product row (and variant row if exists) ----
            product = Product.objects.select_for_update().get(
                id=product_id, is_active=True
            )

            variant = None
            if variant_id:
                variant = ProductVariant.objects.select_for_update().get(
                    id=variant_id, product=product
                )

            # ---- Stock check with preorder rule ----
            # If variant exists, use variant stock; else product stock.
            stock_available = variant.stock if variant else product.stock

            if not product.is_preorder and stock_available < qty:
                raise ValidationError(
                    f"Insufficient stock for '{product.name}'. Requested {qty}, available {stock_available}."
                )

            # ---- Price integrity: compute from DB ----
            unit_price = _get_effective_price(product, variant)
            line_total = (unit_price * Decimal(qty)).quantize(Decimal("0.01"))
            subtotal += line_total

            validated_items.append(
                {
                    "product": product,
                    "variant": variant,
                    "qty": qty,
                    "unit_price": unit_price,
                    "line_total": line_total,
                }
            )

        # Shipping: keep simple for now; later add shipping/tax services
        total = subtotal

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            email=email,
            status="pending",
            subtotal=subtotal,
            total=total,
            shipping_name=shipping.get("name", ""),
            shipping_line1=shipping.get("line1", ""),
            shipping_city=shipping.get("city", ""),
            shipping_postcode=shipping.get("postcode", ""),
            shipping_country=shipping.get("country", ""),
        )

        for item in validated_items:
            product = item["product"]
            variant = item["variant"]

            sku = variant.sku if variant else ""
            display_name = product.name + (f" ({variant.name})" if variant else "")

            OrderItem.objects.create(
                order=order,
                product=product,
                variant=variant,
                product_name=display_name,
                sku=sku,
                unit_price=item["unit_price"],
                qty=item["qty"],
                line_total=item["line_total"],
            )

        log_event(
            event_type="order_created",
            entity_type="order",
            entity_id=order.id,
            user=request.user if request.user.is_authenticated else None,
            metadata={"total": str(order.total), "items": len(validated_items)},
        )

        clear(request.session)
        return order
