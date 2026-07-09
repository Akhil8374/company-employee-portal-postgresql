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
    )

    module = models.CharField(
        max_length=50,
        choices=MODULE_CHOICES,
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

    timestamp = models.DateTimeField(auto_now_add=True)

    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        username = self.user.username if self.user else "system"
        return f"[{self.timestamp}] {username} - {self.action} {self.module}"
