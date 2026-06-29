from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.serializers import AuditLogSerializer
from api.responses import SuccessResponse
from api.permissions import IsAdmin
from audit_logs.models import AuditLog


class AuditLogListView(APIView):
    """
    GET /api/v1/audit-logs/ — List all audit logs (Admin only)

    Supports query parameter filtering:
    - ?action=CREATE
    - ?module=EMPLOYEE
    - ?user=<user_id>
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        queryset = AuditLog.objects.select_related("user").all()

        # Apply filters from query params
        action = request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action.upper())

        module = request.query_params.get("module")
        if module:
            queryset = queryset.filter(module=module.upper())

        user_id = request.query_params.get("user")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Limit results for performance
        queryset = queryset[:100]

        serializer = AuditLogSerializer(queryset, many=True)
        return SuccessResponse(
            data=serializer.data,
            message="Audit logs retrieved successfully",
        )
