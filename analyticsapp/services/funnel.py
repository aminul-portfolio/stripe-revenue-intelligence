from django.utils import timezone

from wishlist.models import Wishlist
from orders.models import Order


COMPLETED_STATUSES = ("paid", "fulfilled")


def wishlist_funnel(start, end):
    """
    Wishlist → purchase funnel, computed within a single consistent window.

    Notes:
    - wish_users: distinct users who created a wishlist item in the window
    - purchased_users: distinct users (subset of wish_users) who placed a completed order
      (paid/fulfilled) in the same window
    - Adds a small end-boundary grace to avoid microsecond timing issues in CI/tests.
    """
    if timezone.is_naive(start):
        start = timezone.make_aware(start, timezone.get_current_timezone())
    if timezone.is_naive(end):
        end = timezone.make_aware(end, timezone.get_current_timezone())

    end_grace = end + timezone.timedelta(seconds=1)

    wish_users = (
        Wishlist.objects.filter(created_at__gte=start, created_at__lte=end_grace)
        .values_list("user_id", flat=True)
        .distinct()
    )

    purchased_users = (
        Order.objects.filter(
            status__in=COMPLETED_STATUSES,
            created_at__gte=start,
            created_at__lte=end_grace,
            user_id__in=wish_users,
        )
        .values_list("user_id", flat=True)
        .distinct()
    )

    return {
        "wish_users": wish_users.count(),
        "purchased_users": purchased_users.count(),
    }
