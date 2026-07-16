from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from reports.models import GeneratedReport
from api.permissions import IsManagerOrAbove


class ReportListView(generics.ListAPIView):
    """
    GET /api/v1/reports/list/

    Lists all previously generated and stored reports.
    Managers, HR, and Admins can view the full list.
    """
    permission_classes = [IsManagerOrAbove]

    def get_queryset(self):
        queryset = GeneratedReport.objects.all()

        # Optional filters
        report_type = self.request.GET.get('type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        report_format = self.request.GET.get('format')
        if report_format:
            queryset = queryset.filter(format=report_format)

        return queryset

    def get(self, request, *args, **kwargs):
        from api.responses import SuccessResponse
        queryset = self.get_queryset()
        data = list(queryset.values(
            'id', 'report_type', 'format', 'file',
            'generated_by__username', 'generated_at',
        ))
        # Serialize datetimes
        for item in data:
            if item.get('generated_at'):
                item['generated_at'] = str(item['generated_at'])

        return SuccessResponse(
            data=data,
            message="Reports retrieved successfully",
        )
