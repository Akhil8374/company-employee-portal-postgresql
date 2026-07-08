from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Enterprise audit logging model.
    Tracks every significant action in the system.
    """

    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("PASSWORD_CHANGE", "Password Change"),
        ("PASSWORD_RESET", "Password Reset"),
        ("TOKEN_BLACKLISTED", "Token Blacklisted"),
        ("UNAUTHORIZED_ACCESS", "Unauthorized Access"),
        ("PERMISSION_DENIED", "Permission Denied"),
    ]

    MODULE_CHOICES = [
        ("EMPLOYEE", "Employee"),
        ("DEPARTMENT", "Department"),
        ("AUTH", "Authentication"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
    )

    module = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
        db_index=True,
    )

    object_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Primary key of the affected object.",
    )

    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional details about the action (e.g., changed fields).",
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    request_method = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="HTTP method (GET, POST, PUT, DELETE, etc.).",
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        username = self.user.username if self.user else "system"
        return f"[{self.timestamp}] {username} - {self.action} {self.module}"


class BlockedIP(models.Model):
    """
    Stores IP addresses that are blocked from accessing the system.
    Used by IPRestrictionMiddleware.
    """

    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.TextField(
        blank=True,
        help_text="Reason for blocking this IP.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"

    def __str__(self):
        return f"{self.ip_address} — {self.reason[:50]}"

