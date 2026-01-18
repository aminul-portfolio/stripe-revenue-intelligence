from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .services.cart import cart_summary, add_to_cart, set_qty, remove, clear


def cart_view(request):
    return render(request, "cart/cart.html", {"cart": cart_summary(request.session)})


@require_POST
def cart_add(request):
    try:
        product_id = int(request.POST.get("product_id"))
        variant_id = request.POST.get("variant_id") or None
        variant_id = int(variant_id) if variant_id else None
        qty = int(request.POST.get("qty", 1))

        add_to_cart(
            request.session,
            product_id=product_id,
            qty=qty,
            variant_id=variant_id,
        )
        messages.success(request, "Added to cart.")
    except (TypeError, ValueError):
        messages.error(request, "Invalid quantity or product selection.")
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception:
        # Safety: do not leak internal details to users
        messages.error(request, "Could not add item to cart. Please try again.")

    return redirect("cart")


@require_POST
def cart_update(request):
    try:
        key = request.POST.get("key", "")
        qty = int(request.POST.get("qty", 0))

        set_qty(request.session, key=key, qty=qty)
        messages.success(request, "Cart updated.")
    except (TypeError, ValueError):
        messages.error(request, "Invalid quantity.")
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception:
        messages.error(request, "Could not update cart. Please try again.")

    return redirect("cart")


@require_POST
def cart_remove(request):
    try:
        key = request.POST.get("key", "")
        remove(request.session, key=key)
        messages.success(request, "Item removed.")
    except Exception:
        messages.error(request, "Could not remove item. Please try again.")
    return redirect("cart")


@require_POST
def cart_clear(request):
    try:
        clear(request.session)
        messages.success(request, "Cart cleared.")
    except Exception:
        messages.error(request, "Could not clear cart. Please try again.")
    return redirect("cart")
