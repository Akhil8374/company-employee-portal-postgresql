from rest_framework.exceptions import NotFound, ValidationError

from api.repositories import EmployeeRepository


class EmployeeService:
    """
    Business logic layer for Employee operations.
    Views should delegate all logic to this service.
    """

    def __init__(self):
        self.repository = EmployeeRepository()

    def list_employees(self):
        """Get all employees (optimized for list views)."""
        return self.repository.get_optimized_list()

    def get_employee(self, pk):
        """
        Get a single employee by ID.
        Raises NotFound if employee doesn't exist.
        """
        employee = self.repository.get_by_id(pk)
        if employee is None:
            raise NotFound(f"Employee with id {pk} not found.")
        return employee

    def create_employee(self, validated_data):
        """
        Create a new employee.
        Business rules can be added here (e.g., duplicate checks).
        """
        # Check for duplicate employee_id
        from employees.models import Employee

        employee_id = validated_data.get("employee_id")
        if employee_id and Employee.objects.filter(employee_id=employee_id).exists():
            raise ValidationError(
                {"employee_id": f"Employee with ID '{employee_id}' already exists."}
            )

        # Check for duplicate email
        email = validated_data.get("email")
        if email and Employee.objects.filter(email=email).exists():
            raise ValidationError(
                {"email": f"Employee with email '{email}' already exists."}
            )

        return self.repository.create(validated_data)

    def update_employee(self, pk, validated_data):
        """
        Update an existing employee.
        Raises NotFound if employee doesn't exist.
        """
        employee = self.get_employee(pk)

        # Check for duplicate email (exclude current employee)
        from employees.models import Employee

        email = validated_data.get("email")
        if email and Employee.objects.filter(email=email).exclude(pk=pk).exists():
            raise ValidationError(
                {"email": f"Employee with email '{email}' already exists."}
            )

        return self.repository.update(employee, validated_data)

    def delete_employee(self, pk):
        """
        Delete an employee.
        Raises NotFound if employee doesn't exist.
        """
        employee = self.get_employee(pk)
        self.repository.delete(employee)

    def get_employees_by_department(self, department_id):
        """Get all employees in a specific department."""
        return self.repository.get_by_department(department_id)
