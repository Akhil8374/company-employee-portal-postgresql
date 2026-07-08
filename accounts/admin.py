from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, PasswordResetToken
from .security import SecurityLog


# ─────────────────────────────────────────────────────────────────────────────
# User Admin
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "role", "employee_id", "is_active", "date_joined"]
    list_filter  = ["role", "is_active", "is_staff"]
    search_fields = ["username", "email", "employee_id"]
    ordering = ["-date_joined"]

    fieldsets = UserAdmin.fieldsets + (
        ("HRMS Info", {
            "fields": ("role", "employee_id", "phone", "profile_image"),
        }),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Password Reset Token Admin
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display  = ["user", "token", "created_at", "expires_at", "is_used"]
    list_filter   = ["is_used"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["token", "created_at", "expires_at"]
    ordering = ["-created_at"]


# ─────────────────────────────────────────────────────────────────────────────
# Security Log Admin
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display  = ["timestamp", "user", "action", "status", "ip_address"]
    list_filter   = ["action", "status"]
    search_fields = ["user__username", "ip_address", "action"]
    readonly_fields = ["user", "action", "status", "ip_address", "timestamp", "details"]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        return False  # Logs are system-generated only

    def has_change_permission(self, request, obj=None):
        return False  # Immutable — read-only in admin