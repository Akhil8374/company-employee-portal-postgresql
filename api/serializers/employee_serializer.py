from rest_framework import serializers

from employees.models import Employee


class EmployeeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Employee list views.
    Returns basic fields + department name (read-only).
    """
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "designation",
            "department",
            "department_name",
            "status",
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Full serializer for Employee CRUD operations.
    - Write: accepts department as FK (integer ID)
    - Read: includes nested department details + manager info
    """
    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    manager_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "salary",
            "joining_date",
            "designation",
            "department",
            "department_name",
            "manager",
            "manager_name",
            "profile_photo",
            "resume",
            "aadhaar_document",
            "pan_document",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None


class EmployeeV2Serializer(serializers.ModelSerializer):
    """
    V2 serializer — expanded view with full department details
    and manager details (nested).
    """
    department_details = serializers.SerializerMethodField()
    manager_details = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "salary",
            "joining_date",
            "designation",
            "department",
            "department_details",
            "manager",
            "manager_details",
            "profile_photo",
            "resume",
            "aadhaar_document",
            "pan_document",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_department_details(self, obj):
        if obj.department:
            return {
                "id": obj.department.id,
                "name": obj.department.name,
                "description": obj.department.description,
            }
        return None

    def get_manager_details(self, obj):
        if obj.manager:
            return {
                "id": obj.manager.id,
                "employee_id": obj.manager.employee_id,
                "first_name": obj.manager.first_name,
                "last_name": obj.manager.last_name,
                "email": obj.manager.email,
                "designation": obj.manager.designation,
            }
        return None
