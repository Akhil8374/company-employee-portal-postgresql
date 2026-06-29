from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only admin for audit logs."""

    list_display = (
        "timestamp",
        "user",
        "action",
        "module",
        "object_id",
        "ip_address",
    )

    list_filter = (
        "action",
        "module",
        "timestamp",
    )

    search_fields = (
        "user__username",
        "object_id",
        "ip_address",
    )

    readonly_fields = (
        "user",
        "action",
        "module",
        "object_id",
        "details",
        "timestamp",
        "ip_address",
    )

    ordering = ("-timestamp",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
