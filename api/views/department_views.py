from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from api.services import DepartmentService
from api.serializers import (
    DepartmentSerializer,
    DepartmentWithEmployeesSerializer,
)
from api.responses import SuccessResponse, ErrorResponse
from audit_logs.utils import create_audit_log, get_client_ip


class DepartmentListCreateView(APIView):
    """
    GET  /api/v1/departments/ — List all departments
    POST /api/v1/departments/ — Create a new department
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DepartmentService()

    @method_decorator(cache_page(60 * 30))
    def get(self, request):
        departments = self.service.list_departments()

        paginator = Paginator(departments, 10)

        page_number = request.GET.get("page", 1)

        page_obj = paginator.get_page(page_number)

        serializer = DepartmentSerializer(page_obj.object_list, many=True)
        return SuccessResponse(
    data={
        "departments": serializer.data,
        "pagination": {
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_records": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous_page": page_obj.previous_page_number() if page_obj.has_previous() else None,
        },
    },
    message="Departments retrieved successfully",
)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        department = serializer.save()

        create_audit_log(
            user=request.user,
            action="CREATE",
            module="DEPARTMENT",
            object_id=department.pk,
            details=serializer.data,
            ip_address=get_client_ip(request),
    )
        
        return SuccessResponse(
            data=DepartmentSerializer(department).data,
            message="Department created successfully",
            status_code=status.HTTP_201_CREATED,
    )

class DepartmentDetailView(APIView):
    """
    GET    /api/v1/departments/{id}/ — Retrieve a department
    PUT    /api/v1/departments/{id}/ — Update a department
    DELETE /api/v1/departments/{id}/ — Delete a department
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DepartmentService()

    def get(self, request, pk):
        department = self.service.get_department(pk)
        serializer = DepartmentSerializer(department)
        return SuccessResponse(
            data=serializer.data,
            message="Department retrieved successfully",
        )

    def put(self, request, pk):
        department = self.service.get_department(pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_department = serializer.save()

        # Audit log
        create_audit_log(
            user=request.user,
            action="UPDATE",
            module="DEPARTMENT",
            object_id=updated_department.pk,
            details=serializer.validated_data,
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            data=DepartmentSerializer(updated_department).data,
            message="Department updated successfully",
        )

    def delete(self, request, pk):
        department = self.service.get_department(pk)
        department_data = DepartmentSerializer(department).data
        self.service.delete_department(pk)

        # Audit log
        create_audit_log(
            user=request.user,
            action="DELETE",
            module="DEPARTMENT",
            object_id=pk,
            details=department_data,
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            message="Department deleted successfully",
            status_code=status.HTTP_200_OK,
        )


class DepartmentEmployeesView(APIView):
    """
    GET /api/v1/departments/{id}/employees/ — Get department with nested employees
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DepartmentService()

    def get(self, request, pk):
        department = self.service.get_department_with_employees(pk)
        serializer = DepartmentWithEmployeesSerializer(department)
        return SuccessResponse(
            data=serializer.data,
            message="Department employees retrieved successfully",
        )
