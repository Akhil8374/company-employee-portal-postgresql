from rest_framework import serializers

from employees.models import Department, Employee


class DepartmentSerializer(serializers.ModelSerializer):
    """Standard Department serializer for CRUD operations."""

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DepartmentWithEmployeesSerializer(serializers.ModelSerializer):
    """
    Nested serializer — Department with its employees list.

    Output:
    {
        "id": 1,
        "name": "Engineering",
        "employees": [
            { "id": 1, "name": "Ajay", ... }
        ]
    }
    """
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id",
            "name",
            "description",
            "employees",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_employees(self, obj):
        """Return nested employee list for this department."""
        employees = obj.employee_set.all()
        return [
            {
                "id": emp.id,
                "employee_id": emp.employee_id,
                "name": f"{emp.first_name} {emp.last_name}",
                "email": emp.email,
                "designation": emp.designation,
                "status": emp.status,
            }
            for emp in employees
        ]
