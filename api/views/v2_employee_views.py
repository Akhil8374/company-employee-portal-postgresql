from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.services import EmployeeService
from api.serializers import EmployeeV2Serializer
from api.responses import SuccessResponse


class EmployeeV2ListCreateView(APIView):
    """
    GET  /api/v2/employees/ — List employees with expanded details
    POST /api/v2/employees/ — Create employee (same as V1)

    V2 returns department details and manager details as nested objects.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmployeeService()

    def get(self, request):
        employees = self.service.list_employees()
        serializer = EmployeeV2Serializer(employees, many=True)
        return SuccessResponse(
            data=serializer.data,
            message="Employees retrieved successfully (V2)",
        )

    def post(self, request):
        serializer = EmployeeV2Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        return SuccessResponse(
            data=EmployeeV2Serializer(employee).data,
            message="Employee created successfully (V2)",
            status_code=201,
        )


class EmployeeV2DetailView(APIView):
    """
    GET    /api/v2/employees/{id}/ — Retrieve with expanded details
    PUT    /api/v2/employees/{id}/ — Update employee
    DELETE /api/v2/employees/{id}/ — Delete employee

    V2 includes full department + manager nested objects.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = EmployeeService()

    def get(self, request, pk):
        employee = self.service.get_employee(pk)
        serializer = EmployeeV2Serializer(employee)
        return SuccessResponse(
            data=serializer.data,
            message="Employee retrieved successfully (V2)",
        )

    def put(self, request, pk):
        employee = self.service.get_employee(pk)
        serializer = EmployeeV2Serializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_employee = serializer.save()
        return SuccessResponse(
            data=EmployeeV2Serializer(updated_employee).data,
            message="Employee updated successfully (V2)",
        )

    def delete(self, request, pk):
        self.service.delete_employee(pk)
        return SuccessResponse(
            message="Employee deleted successfully (V2)",
        )
