from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse, Http404

from .models import EmployeeDocument
from .serializers import EmployeeDocumentSerializer
from api.permissions import IsHROrAdmin

class EmployeeDocumentListCreateView(generics.ListCreateAPIView):
    """
    GET  : List all employee documents (filtered by role)
    POST : Upload a new employee document
    """
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "HR"]:
            return EmployeeDocument.objects.all()
        # Employee can only view their own documents. Assuming employee is linked via email or similar
        # Since Employee model has email matching User model's email:
        return EmployeeDocument.objects.filter(employee__email=user.email)

class EmployeeDocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    : Retrieve document details
    DELETE : Delete document (HR/Admin only)
    """
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "HR"]:
            return EmployeeDocument.objects.all()
        return EmployeeDocument.objects.filter(employee__email=user.email)

    def destroy(self, request, *args, **kwargs):
        if request.user.role not in ["ADMIN", "HR"]:
            return Response(
                {"detail": "Only HR and Admin can delete documents."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class EmployeeDocumentDownloadView(generics.GenericAPIView):
    """
    Download an employee document with permission check.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["ADMIN", "HR"]:
            return EmployeeDocument.objects.all()
        return EmployeeDocument.objects.filter(employee__email=user.email)

    def get(self, request, pk):
        try:
            document = self.get_queryset().get(pk=pk)

            if not document.file:
                raise Http404("Document file not found.")

            response = FileResponse(
                document.file.open("rb"),
                as_attachment=True,
                filename=document.file.name.split("/")[-1],
            )
            # Proper Response Headers
            response['Content-Disposition'] = f'attachment; filename="{document.file.name.split("/")[-1]}"'
            return response

        except EmployeeDocument.DoesNotExist:
            return Response(
                {"detail": "Document not found or you do not have permission to access it."},
                status=status.HTTP_404_NOT_FOUND,
            )