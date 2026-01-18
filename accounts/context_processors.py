from .services.roles import get_role


def user_role(request):
    return {"user_role": get_role(getattr(request, "user", None))}
