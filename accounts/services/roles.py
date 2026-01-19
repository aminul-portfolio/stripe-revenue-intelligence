from __future__ import annotations

from typing import Any

from django.contrib.auth.models import Group


def get_role(user: Any) -> str | None:
    if not getattr(user, "is_authenticated", False):
        return None

    prof = getattr(user, "role_profile", None)
    if prof and getattr(prof, "role", None):
        return prof.role

    # Safe fallback for authenticated users without a profile (should be rare)
    return "customer"


def is_admin(user: Any) -> bool:
    return bool(getattr(user, "is_superuser", False) or get_role(user) == "admin")


def is_backoffice(user: Any) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if is_admin(user):
        return True
    return get_role(user) in {"ops", "analyst"}


def set_role(user: Any, role: str) -> None:
    """
    Test/support helper: set a user's role in the project's canonical role storage.

    Canonical storage (this project):
      - user.role_profile.role

    Also aligns Django flags:
      - ops/analyst/admin => is_staff=True
      - admin => is_superuser=True
      - customer => is_staff=False, is_superuser=False

    Fallback (only if no role_profile relation exists):
      - Django Group named role ("customer", "ops", "analyst", "admin")
    """
    role = (role or "").strip().lower()
    if role not in {"customer", "ops", "analyst", "admin"}:
        raise ValueError(f"Invalid role: {role}")

    # Align flags first (common in view protection)
    if role == "admin":
        user.is_staff = True
        user.is_superuser = True
    elif role in {"ops", "analyst"}:
        user.is_staff = True
        user.is_superuser = False
    else:  # customer
        user.is_staff = False
        user.is_superuser = False

    # Persist flags even if profile logic fails
    user.save(update_fields=["is_staff", "is_superuser"])

    # Canonical: role_profile.role
    prof = getattr(user, "role_profile", None)
    if prof is not None and hasattr(prof, "role"):
        prof.role = role
        prof.save(update_fields=["role"])
        return

    # Try to create role_profile if there's a reverse one-to-one relation
    # e.g., RoleProfile(user=..., role=...)
    try:
        rel = user._meta.get_field("role_profile")
        model = rel.related_model
        model.objects.update_or_create(user=user, defaults={"role": role})
        return
    except Exception:
        # Last resort: Groups
        group, _ = Group.objects.get_or_create(name=role)
        user.groups.remove(
            *Group.objects.filter(name__in=["customer", "ops", "analyst", "admin"])
        )
        user.groups.add(group)
