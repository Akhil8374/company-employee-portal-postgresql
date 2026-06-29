from rest_framework.exceptions import NotFound

from api.repositories import DepartmentRepository


class DepartmentService:
    """
    Business logic layer for Department operations.
    Views should delegate all logic to this service.
    """

    def __init__(self):
        self.repository = DepartmentRepository()

    def list_departments(self):
        """Get all departments."""
        return self.repository.get_all()

    def get_department(self, pk):
        """
        Get a single department by ID.
        Raises NotFound if department doesn't exist.
        """
        department = self.repository.get_by_id(pk)
        if department is None:
            raise NotFound(f"Department with id {pk} not found.")
        return department

    def create_department(self, validated_data):
        """Create a new department."""
        return self.repository.create(validated_data)

    def update_department(self, pk, validated_data):
        """
        Update an existing department.
        Raises NotFound if department doesn't exist.
        """
        department = self.get_department(pk)
        return self.repository.update(department, validated_data)

    def delete_department(self, pk):
        """
        Delete a department.
        Raises NotFound if department doesn't exist.
        """
        department = self.get_department(pk)
        self.repository.delete(department)

    def get_department_with_employees(self, pk):
        """
        Get a department with all its employees (prefetched).
        Raises NotFound if department doesn't exist.
        """
        department = self.repository.get_with_employees(pk=pk)
        if department is None:
            raise NotFound(f"Department with id {pk} not found.")
        return department
