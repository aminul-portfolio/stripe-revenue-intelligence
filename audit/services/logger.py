from ..models import AuditLog


def log_event(
    *, event_type: str, entity_type: str, entity_id, user=None, metadata=None
):
    AuditLog.objects.create(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=str(entity_id),
        user=user if getattr(user, "is_authenticated", False) else None,
        metadata=metadata or {},
    )
