from rest_framework import serializers

from accounts.models import User


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


class LoginSerializer(serializers.Serializer):
    """Serializer for custom login request."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout request — requires refresh token."""
    refresh = serializers.CharField(required=True)
