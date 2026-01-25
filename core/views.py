from django.shortcuts import render
from products.models import Product
from django.http import HttpResponse

def home(request):
    featured = Product.objects.filter(is_active=True).order_by("-created_at")[:6]
    return render(request, "core/home.html", {"featured": featured})


def healthz(request):
    """
    Lightweight health endpoint for container/runtime checks.
    Intentionally does not touch DB to avoid masking DB failures.
    """
    return HttpResponse("ok", content_type="text/plain")
