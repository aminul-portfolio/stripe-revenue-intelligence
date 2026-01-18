from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from orders.models import Order
from wishlist.models import Wishlist
from subscriptions.models import Subscription


@login_required
def account_dashboard(request):
    # Orders: if user is attached use it, otherwise show none (privacy-safe)
    orders = Order.objects.filter(user=request.user).order_by("-created_at")[:10]

    wishlist_items = (
        Wishlist.objects.filter(user=request.user)
        .select_related("product")
        .order_by("-created_at")[:12]
    )

    subs = Subscription.objects.filter(user=request.user).order_by("-created_at")[:10]

    return render(
        request,
        "accounts/account_dashboard.html",
        {
            "orders": orders,
            "wishlist_items": wishlist_items,
            "subs": subs,
        },
    )
