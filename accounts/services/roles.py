def get_role(user):
    if not getattr(user, "is_authenticated", False):
        return None

    prof = getattr(user, "role_profile", None)
    if prof and getattr(prof, "role", None):
        return prof.role

    # Safe fallback for authenticated users without a profile (should be rare)
    return "customer"


def is_admin(user) -> bool:
    return bool(getattr(user, "is_superuser", False) or get_role(user) == "admin")


def is_backoffice(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if is_admin(user):
        return True
    return get_role(user) in {"ops", "analyst"}
