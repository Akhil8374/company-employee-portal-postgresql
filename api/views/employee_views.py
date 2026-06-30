from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from api.services import EmployeeService
from api.serializers import EmployeeSerializer, EmployeeListSerializer
from api.responses import SuccessResponse
from audit_logs.utils import create_audit_log, get_client_ip


class EmployeeListCreateView(APIView):
    """
    GET  /api/v1/employees/ — List all employees
    POST /api/v1/employees/ — Create a new employee
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmployeeService()

    @method_decorator(cache_page(60 * 5))
    def get(self, request):
        employees = self.service.list_employees()
        serializer = EmployeeListSerializer(employees, many=True)

        return SuccessResponse(
            data=serializer.data,
            message="Employees retrieved successfully",
        )

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        employee = serializer.save()

        create_audit_log(
            user=request.user,
            action="CREATE",
            module="EMPLOYEE",
            object_id=employee.pk,
            details=serializer.data,
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            data=EmployeeSerializer(employee).data,
            message="Employee created successfully",
            status_code=status.HTTP_201_CREATED,
        )


class EmployeeDetailView(APIView):
    """
    GET Employee
    PUT Employee
    DELETE Employee
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmployeeService()

    def get(self, request, pk):
        employee = self.service.get_employee(pk)

        return SuccessResponse(
            data=EmployeeSerializer(employee).data,
            message="Employee retrieved successfully",
        )

    def put(self, request, pk):
        employee = self.service.get_employee(pk)

        serializer = EmployeeSerializer(
            employee,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        updated_employee = serializer.save()

        create_audit_log(
            user=request.user,
            action="UPDATE",
            module="EMPLOYEE",
            object_id=updated_employee.pk,
            details=serializer.validated_data,
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            data=EmployeeSerializer(updated_employee).data,
            message="Employee updated successfully",
        )

    def delete(self, request, pk):

        employee = self.service.get_employee(pk)

        employee_data = EmployeeSerializer(employee).data

        self.service.delete_employee(pk)

        create_audit_log(
            user=request.user,
            action="DELETE",
            module="EMPLOYEE",
            object_id=pk,
            details=employee_data,
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            message="Employee deleted successfully",
            status_code=status.HTTP_200_OK,
        )


class EmployeeAnalyticsView(APIView):
    """
    Advanced ORM Analytics Dashboard
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmployeeService()

    def get(self, request):

        data = {
            "top_10_highest_paid": [
                {
                    "employee_id": emp.employee_id,
                    "name": f"{emp.first_name} {emp.last_name}",
                    "salary": emp.salary,
                    "department": emp.department.name,
                }
                for emp in self.service.top_10_highest_paid()
            ],

            "department_employee_count":
                list(self.service.department_employee_count()),

            "salary_statistics":
                self.service.monthly_salary_statistics(),

            "employees_joined_this_month": [
                {
                    "employee_id": emp.employee_id,
                    "name": f"{emp.first_name} {emp.last_name}",
                }
                for emp in self.service.employees_joined_this_month()
            ],
        }

        return SuccessResponse(
            data=data,
            message="Employee Analytics Generated Successfully",
        )