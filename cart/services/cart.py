from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError

from products.models import Product, ProductVariant

CART_SESSION_KEY = "purelaka_cart"


def _get_cart(session):
    return session.get(CART_SESSION_KEY, {})


def _save_cart(session, cart: dict) -> None:
    session[CART_SESSION_KEY] = cart
    session.modified = True


def _make_key(product_id: int, variant_id: Optional[int]) -> str:
    return f"{product_id}:{variant_id or ''}"


def _resolve_product_variant(*, product_id: int, variant_id: Optional[int]):
    """
    Resolve the product + optional variant from DB.
    Returns (product, variant, unit_price, available_stock, is_preorder).
    """
    product = Product.objects.filter(id=product_id).first()
    if not product:
        raise ValidationError("Product not found.")

    is_preorder = bool(getattr(product, "is_preorder", False))

    variant = None
    unit_price = product.price
    available_stock = int(getattr(product, "stock", 0) or 0)

    if variant_id:
        variant = ProductVariant.objects.filter(id=variant_id, product=product).first()
        if not variant:
            raise ValidationError("Variant not found for this product.")
        # Prefer your model helper if present
        if hasattr(variant, "effective_price"):
            unit_price = variant.effective_price()
        elif getattr(variant, "price_override", None) is not None:
            unit_price = variant.price_override
        available_stock = int(getattr(variant, "stock", 0) or 0)

    return product, variant, Decimal(str(unit_price)), available_stock, is_preorder


def _validate_qty(*, qty: int, available_stock: int, is_preorder: bool) -> None:
    if qty < 1:
        raise ValidationError("Quantity must be at least 1.")

    if is_preorder:
        return

    if qty > available_stock:
        raise ValidationError("Not enough stock.")


def cart_summary(session):
    """
    Display-only cart summary.
    Checkout/order creation MUST still recalculate totals from DB (Sprint 3 Step 1).
    """
    cart = _get_cart(session)
    items = []
    total = Decimal("0.00")

    for key, row in cart.items():
        qty = int(row.get("qty", 0))
        if qty <= 0:
            continue

        product_id = row.get("product_id")
        variant_id = row.get("variant_id")

        product = Product.objects.filter(id=product_id).first()
        if not product:
            continue

        variant = None
        price = Decimal(str(product.price))

        if variant_id:
            variant = ProductVariant.objects.filter(
                id=variant_id, product=product
            ).first()
            if variant:
                if hasattr(variant, "effective_price"):
                    price = Decimal(str(variant.effective_price()))
                elif getattr(variant, "price_override", None) is not None:
                    price = Decimal(str(variant.price_override))

        line_total = price * qty
        total += line_total
        items.append(
            {
                "key": key,
                "product": product,
                "variant": variant,
                "qty": qty,
                "price": price,
                "line_total": line_total,
            }
        )

    return {"items": items, "total": total, "count": sum(i["qty"] for i in items)}


def add_to_cart(session, product_id: int, qty: int = 1, variant_id=None):
    """
    Adds to cart with validation:
    - qty must be >= 1
    - if not preorder, qty must not exceed stock (variant stock if present)
    """
    qty = int(qty)
    variant_id = int(variant_id) if variant_id not in (None, "") else None

    product, variant, unit_price, available_stock, is_preorder = (
        _resolve_product_variant(product_id=product_id, variant_id=variant_id)
    )

    cart = _get_cart(session)
    key = _make_key(product_id, variant_id)

    row = cart.get(key, {"product_id": product_id, "variant_id": variant_id, "qty": 0})
    new_qty = int(row.get("qty", 0)) + qty

    _validate_qty(qty=new_qty, available_stock=available_stock, is_preorder=is_preorder)

    row["qty"] = new_qty
    cart[key] = row
    _save_cart(session, cart)


def set_qty(session, key: str, qty: int):
    """
    Sets quantity with validation.
    qty == 0 removes the line (allowed).
    """
    cart = _get_cart(session)
    if key not in cart:
        return

    qty = int(qty)

    if qty <= 0:
        # Removing is allowed
        del cart[key]
        _save_cart(session, cart)
        return

    row = cart[key]
    product_id = row.get("product_id")
    variant_id = row.get("variant_id")

    product, variant, unit_price, available_stock, is_preorder = (
        _resolve_product_variant(product_id=product_id, variant_id=variant_id)
    )

    _validate_qty(qty=qty, available_stock=available_stock, is_preorder=is_preorder)

    row["qty"] = qty
    cart[key] = row
    _save_cart(session, cart)


def remove(session, key: str):
    cart = _get_cart(session)
    if key in cart:
        del cart[key]
        _save_cart(session, cart)


def clear(session):
    _save_cart(session, {})
