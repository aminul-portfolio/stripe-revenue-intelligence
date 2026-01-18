from .services.cart import cart_summary as cart_summary_service


def cart_summary(request):
    try:
        return {"cart": cart_summary_service(request.session)}
    except Exception:
        return {"cart": None}
