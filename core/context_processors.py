from django.conf import settings


def payments_flags(request):
    return {
        "PAYMENTS_USE_STRIPE": bool(getattr(settings, "PAYMENTS_USE_STRIPE", False)),
        # Optional (only if you want to access it in templates)
        "STRIPE_PUBLISHABLE_KEY": getattr(settings, "STRIPE_PUBLISHABLE_KEY", ""),
    }
