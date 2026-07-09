from rest_framework import serializers
from .models import EmployeeDocument


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDocument
        fields = [
            "id",
            "employee",
            "document_name",
            "document_type",
            "file",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at"]


class EmployeeImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith(".xlsx"):
            raise serializers.ValidationError(
                "Only .xlsx Excel files are allowed."
            )

        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size cannot exceed 5 MB."
            )

        return value