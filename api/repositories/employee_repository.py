from employees.models import Employee


class EmployeeRepository:
    """
    Data access layer for Employee model.
    All database queries for employees go through this class.
    """

    @staticmethod
    def get_all():
        """Get all employees with related department (optimized)."""
        return Employee.objects.select_related("department").all()

    @staticmethod
    def get_by_id(pk):
        """Get a single employee by primary key, or None."""
        try:
            return Employee.objects.select_related("department").get(pk=pk)
        except Employee.DoesNotExist:
            return None

    @staticmethod
    def create(validated_data):
        """Create and return a new employee."""
        return Employee.objects.create(**validated_data)

    @staticmethod
    def update(instance, validated_data):
        """Update an existing employee instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def delete(instance):
        """Delete an employee instance."""
        instance.delete()

    @staticmethod
    def get_by_department(department_id):
        """Get all employees in a specific department."""
        return Employee.objects.select_related("department").filter(
            department_id=department_id
        )

    @staticmethod
    def get_optimized_list():
        """
        Optimized query for list views.
        Uses select_related + only to minimize DB load.
        """
        return (
            Employee.objects.select_related("department")
            .only(
                "id",
                "employee_id",
                "first_name",
                "last_name",
                "email",
                "designation",
                "department__id",
                "department__name",
                "status",
            )
        )

    @staticmethod
    def filter_queryset(queryset, filters):
        """Apply dynamic filters to a queryset."""
        if filters.get("department"):
            queryset = queryset.filter(department_id=filters["department"])
        if filters.get("status") is not None:
            queryset = queryset.filter(status=filters["status"])
        if filters.get("search"):
            search = filters["search"]
            queryset = queryset.filter(
                models.Q(first_name__icontains=search)
                | models.Q(last_name__icontains=search)
                | models.Q(email__icontains=search)
                | models.Q(employee_id__icontains=search)
            )
        return queryset
