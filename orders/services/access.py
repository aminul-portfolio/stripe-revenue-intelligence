from django.http import Http404

from accounts.services.roles import is_admin, is_backoffice


def assert_can_access_order(request, order) -> None:
    """
    Access rules:
      - Admin always allowed
      - Backoffice (staff + ops/analyst) allowed
      - Customer allowed only for own order
      - Guest/session allowed only if order.id is in session allowlist
      - Otherwise: 404 to hide existence (prevents ID enumeration)
    """
    # Backoffice / Admin access
    if request.user.is_authenticated:
        if is_admin(request.user):
            return
        if request.user.is_staff and is_backoffice(request.user):
            return

    # Customer access (owned order)
    if (
        request.user.is_authenticated
        and getattr(order, "user_id", None) == request.user.id
    ):
        return

    # Guest/session access (same browser/session after checkout)
    allowed_ids = request.session.get("order_access_ids", [])
    if order.id in allowed_ids:
        return

    raise Http404()
