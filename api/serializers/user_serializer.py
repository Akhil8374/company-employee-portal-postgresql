from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from accounts.models import User


# ─────────────────────────────────────────────────────────────────────────────
# User Serializer (safe fields only — no password hash exposed)
# ─────────────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """
    User serializer — safe fields only (excludes password hash).
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "employee_id",
            "phone",
            "role",
            "profile_image",
            "is_active",
            "date_joined",
        ]
        read_only_fields = [
            "id",
            "date_joined",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Auth Serializers
# ─────────────────────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    """Serializer for custom login request."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout request — requires refresh token."""
    refresh = serializers.CharField(required=True)


# ─────────────────────────────────────────────────────────────────────────────
# Change Password Serializer
# ─────────────────────────────────────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for Change Password API.
    Validates current password, new password strength, and confirmation match.
    """
    current_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New password and confirm password do not match."}
            )

        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": "New password must be different from the current password."}
            )

        # Run Django's built-in password validators
        validate_password(attrs["new_password"])

        return attrs


# ─────────────────────────────────────────────────────────────────────────────
# Forgot Password Serializer
# ─────────────────────────────────────────────────────────────────────────────

User = get_user_model()


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Forgot Password Serializer.
    Validates that the email exists in the system.
    """
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No user found with this email address."
            )
        return value


# ─────────────────────────────────────────────────────────────────────────────
# Reset Password Serializer
# ─────────────────────────────────────────────────────────────────────────────

class ResetPasswordSerializer(serializers.Serializer):
    """
    Reset Password Serializer.
    Validates the reset token, new password strength, and confirmation match.
    """
    token = serializers.CharField(required=True)

    new_password = serializers.CharField(
        required=True,
        min_length=8,
        write_only=True,
    )

    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        # Run Django's built-in password validators
        validate_password(attrs["new_password"])

        return attrs