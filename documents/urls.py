from django.urls import path

from .views import (
    EmployeeDocumentListCreateView,
    EmployeeDocumentDetailView,
    EmployeeDocumentDownloadView,
)

urlpatterns = [
    path(
        "",
        EmployeeDocumentListCreateView.as_view(),
        name="document-list-create",
    ),
    path(
        "<int:pk>/",
        EmployeeDocumentDetailView.as_view(),
        name="document-detail",
    ),
    path(
        "<int:pk>/download/",
        EmployeeDocumentDownloadView.as_view(),
        name="document-download",
    ),
]