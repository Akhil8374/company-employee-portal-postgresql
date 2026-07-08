from rest_framework import serializers
from django.utils import timezone

from employees.models import Employee
from accounts.validators import (
    validate_employee_id,
    validate_phone_number,
    validate_positive_salary,
    validate_joining_date_not_future,
    SecureImageValidator,
)


# ─────────────────────────────────────────────────────────────────────────────
# Employee List Serializer (lightweight — for list views)
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# Employee Full Serializer (CRUD with validation)
# ─────────────────────────────────────────────────────────────────────────────

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Full serializer for Employee CRUD operations.

    Validation (Module 9):
      - employee_id: EMP + 5 digits format
      - email: unique, valid format
      - phone: exactly 10 digits
      - salary: positive number
      - joining_date: cannot be in the future
      - profile_image: secure upload (JPG/PNG ≤ 2MB)
    """

    department_name = serializers.CharField(
        source="department.name",
        read_only=True,
    )
    manager_name = serializers.SerializerMethodField()

    # ── Validated Fields ─────────────────────────────────────────────────────
    employee_id = serializers.CharField(
        validators=[validate_employee_id],
    )

    phone = serializers.CharField(
        validators=[validate_phone_number],
    )

    salary = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_positive_salary],
    )

    profile_image = serializers.ImageField(
        required=False,
        allow_null=True,
        validators=[SecureImageValidator()],
    )

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
            "profile_image",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_manager_name(self, obj):
        if obj.manager:
            return f"{obj.manager.first_name} {obj.manager.last_name}"
        return None

    def validate_email(self, value):
        """Ensure email is unique (excluding the current instance on update)."""
        instance = self.instance
        qs = Employee.objects.filter(email=value)
        if instance:
            qs = qs.exclude(pk=instance.pk)
        if qs.exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return value

    def validate_joining_date(self, value):
        """Joining date cannot be in the future."""
        validate_joining_date_not_future(value)
        return value


# ─────────────────────────────────────────────────────────────────────────────
# Employee V2 Serializer (expanded nested details)
# ─────────────────────────────────────────────────────────────────────────────

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
            "profile_image",
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
