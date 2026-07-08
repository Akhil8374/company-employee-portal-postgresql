import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser


# ─────────────────────────────────────────────────────────────────────────────
# Custom User Model
# ─────────────────────────────────────────────────────────────────────────────

class User(AbstractUser):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("HR", "HR"),
        ("MANAGER", "Manager"),
        ("EMPLOYEE", "Employee"),
    ]

    employee_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    def __str__(self):
        role = self.role if self.role else "No Role"
        return f"{self.username} ({role})"


# ─────────────────────────────────────────────────────────────────────────────
# Password Reset Token — DB-backed with 15-minute expiry
# ─────────────────────────────────────────────────────────────────────────────

def token_expiry():
    """Returns a timestamp 15 minutes from now."""
    return timezone.now() + timedelta(minutes=15)


class PasswordResetToken(models.Model):
    """
    Stores secure password reset tokens with 15-minute expiry.
    Each token is single-use — marked as used after successful reset.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(default=token_expiry)

    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"

    def __str__(self):
        return f"{self.user.username} — {self.token} (used={self.is_used})"

    @property
    def is_expired(self):
        """Returns True if the token has passed its 15-minute expiry window."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Returns True if the token is not used and not expired."""
        return not self.is_used and not self.is_expired