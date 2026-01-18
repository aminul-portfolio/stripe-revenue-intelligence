from wishlist.models import Wishlist
from orders.models import Order


COMPLETED_STATUSES = ("paid", "fulfilled")


def wishlist_funnel(start, end):
    wish_users = (
        Wishlist.objects.filter(created_at__range=(start, end))
        .values_list("user_id", flat=True)
        .distinct()
    )

    purchased_users = (
        Order.objects.filter(
            status__in=COMPLETED_STATUSES,
            created_at__range=(start, end),
            user_id__in=wish_users,
        )
        .values_list("user_id", flat=True)
        .distinct()
    )

    return {
        "wish_users": wish_users.count(),
        "purchased_users": purchased_users.count(),
    }
