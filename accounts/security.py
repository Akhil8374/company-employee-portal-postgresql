from django.db import models
from django.conf import settings
from django.utils import timezone


class SecurityLog(models.Model):
    """
    Dedicated security audit log model.

    Tracks all security-sensitive events:
      - Login success & failure
      - Password change & reset
      - Unauthorized access attempts
      - Permission denied events
      - Token blacklisting

    This is separate from the general AuditLog to enable focused
    security monitoring, alerting, and compliance reporting.
    """

    # ── Action Choices ────────────────────────────────────────────────────────
    ACTION_LOGIN_SUCCESS    = "LOGIN_SUCCESS"
    ACTION_LOGIN_FAILURE    = "LOGIN_FAILURE"
    ACTION_LOGOUT           = "LOGOUT"
    ACTION_PASSWORD_CHANGE  = "PASSWORD_CHANGE"
    ACTION_PASSWORD_RESET   = "PASSWORD_RESET"
    ACTION_UNAUTHORIZED     = "UNAUTHORIZED_ACCESS"
    ACTION_PERMISSION_DENIED = "PERMISSION_DENIED"
    ACTION_TOKEN_BLACKLISTED = "TOKEN_BLACKLISTED"

    ACTION_CHOICES = [
        (ACTION_LOGIN_SUCCESS,     "Login Success"),
        (ACTION_LOGIN_FAILURE,     "Login Failure"),
        (ACTION_LOGOUT,            "Logout"),
        (ACTION_PASSWORD_CHANGE,   "Password Change"),
        (ACTION_PASSWORD_RESET,    "Password Reset"),
        (ACTION_UNAUTHORIZED,      "Unauthorized Access"),
        (ACTION_PERMISSION_DENIED, "Permission Denied"),
        (ACTION_TOKEN_BLACKLISTED, "Token Blacklisted"),
    ]

    # ── Status Choices ────────────────────────────────────────────────────────
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILURE = "FAILURE"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILURE, "Failure"),
    ]

    # ── Fields ────────────────────────────────────────────────────────────────
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="security_logs",
        help_text="User who performed the action (null for anonymous attempts).",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        db_index=True,
        help_text="IP address from which the action was performed.",
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        db_index=True,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_SUCCESS,
        db_index=True,
    )

    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context (e.g., attempted username, endpoint, reason).",
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Security Log"
        verbose_name_plural = "Security Logs"
        indexes = [
            models.Index(fields=["action", "status"]),
            models.Index(fields=["user", "timestamp"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "anonymous"
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {username} — {self.action} ({self.status})"


# ─────────────────────────────────────────────────────────────────────────────
# Utility: create security log entries
# ─────────────────────────────────────────────────────────────────────────────

def log_security_event(
    action: str,
    status: str = SecurityLog.STATUS_SUCCESS,
    user=None,
    ip_address: str = None,
    details: dict = None,
) -> SecurityLog:
    """
    Helper function to create a SecurityLog entry.

    Usage:
        from accounts.security import log_security_event, SecurityLog

        log_security_event(
            action=SecurityLog.ACTION_LOGIN_SUCCESS,
            user=user,
            ip_address=get_client_ip(request),
            details={"username": user.username},
        )
    """
    return SecurityLog.objects.create(
        action=action,
        status=status,
        user=user,
        ip_address=ip_address,
        details=details or {},
    )
