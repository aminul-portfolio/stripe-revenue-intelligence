from functools import wraps

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from accounts.services.roles import get_role, is_admin


def role_required(*allowed_roles, staff_only: bool = False):
    """
    Rules:
      - Unauthenticated -> redirect to LOGIN_URL (?next=...)
      - Admin -> always allowed
      - staff_only=True -> must be user.is_staff (or admin)
      - Role must be in allowed_roles (if provided)
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

            if is_admin(request.user):
                return view_func(request, *args, **kwargs)

            if staff_only and not request.user.is_staff:
                raise PermissionDenied("Staff access required.")

            role = get_role(request.user)
            if allowed_roles and role not in allowed_roles:
                raise PermissionDenied("Access denied.")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
