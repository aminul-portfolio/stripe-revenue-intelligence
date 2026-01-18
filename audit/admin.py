from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event_type", "entity_type", "entity_id", "user")
    list_filter = ("event_type", "entity_type")
    search_fields = ("entity_id",)
    readonly_fields = ("created_at", "metadata")
