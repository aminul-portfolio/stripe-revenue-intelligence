from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserRole

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_role_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.is_superuser:
        role = "admin"
    elif instance.is_staff:
        role = "ops"
    else:
        role = "customer"

    UserRole.objects.get_or_create(user=instance, defaults={"role": role})
