from django.contrib import admin
from django.utils import timezone
from .models import DataQualityIssue


@admin.register(DataQualityIssue)
class DataQualityIssueAdmin(admin.ModelAdmin):
    list_display = ("created_at", "issue_type", "reference_id", "status", "updated_at")
    list_filter = ("issue_type", "status")
    search_fields = ("reference_id", "description")
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at", "resolved_at", "resolved_by")

    actions = ["mark_resolved", "reopen_issue"]

    @admin.action(description="Mark selected issues as resolved")
    def mark_resolved(self, request, queryset):
        now = timezone.now()
        queryset.update(status="resolved", resolved_at=now, resolved_by=request.user)

    @admin.action(description="Reopen selected issues")
    def reopen_issue(self, request, queryset):
        queryset.update(
            status="open", resolved_at=None, resolved_by=None, resolution_notes=""
        )
