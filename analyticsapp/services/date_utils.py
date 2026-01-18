from datetime import timedelta
from django.utils import timezone


def get_range(days: int):
    end = timezone.now()
    start = end - timedelta(days=days)
    return start, end
