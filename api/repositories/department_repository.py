from employees.models import Department


class DepartmentRepository:
    """
    Data access layer for Department model.
    All database queries for departments go through this class.
    """

    @staticmethod
    def get_all():
        """Get all departments."""
        return Department.objects.all()

    @staticmethod
    def get_by_id(pk):
        """Get a single department by primary key, or None."""
        try:
            return Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            return None

    @staticmethod
    def create(validated_data):
        """Create and return a new department."""
        return Department.objects.create(**validated_data)

    @staticmethod
    def update(instance, validated_data):
        """Update an existing department instance."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def delete(instance):
        """Delete a department instance."""
        instance.delete()

    @staticmethod
    def get_with_employees(pk=None):
        """
        Get department(s) with prefetched employees.
        Uses prefetch_related for optimal nested queries.
        """
        queryset = Department.objects.prefetch_related("employee_set")
        if pk:
            try:
                return queryset.get(pk=pk)
            except Department.DoesNotExist:
                return None
        return queryset.all()
