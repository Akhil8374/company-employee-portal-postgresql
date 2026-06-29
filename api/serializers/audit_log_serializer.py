from rest_framework import serializers

from audit_logs.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for AuditLog entries.
    Includes the username for readability.
    """
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        default="system",
    )

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "username",
            "action",
            "module",
            "object_id",
            "details",
            "timestamp",
            "ip_address",
        ]
        read_only_fields = fields
