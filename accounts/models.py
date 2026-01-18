from django.conf import settings
from django.db import models


class UserRole(models.Model):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("analyst", "Analyst"),
        ("ops", "Operations"),
        ("customer", "Customer"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_profile",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    def __str__(self) -> str:
        return f"{self.user} - {self.role}"
