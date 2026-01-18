from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from products.models import Product
from .models import Wishlist


@login_required
def my_wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related("product")
    return render(request, "wishlist/my_wishlist.html", {"items": items})


@login_required
def toggle(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    obj = Wishlist.objects.filter(user=request.user, product=product).first()
    if obj:
        obj.delete()
        return JsonResponse({"liked": False})
    Wishlist.objects.create(user=request.user, product=product)
    return JsonResponse({"liked": True})
