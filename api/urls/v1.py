from django.urls import path

from api.views import (
    # Authentication
    LoginView,
    TokenRefreshView,
    LogoutView,

    # Employees
    EmployeeListCreateView,
    EmployeeDetailView,
    EmployeeImportView,
    EmployeeExportView,
    EmployeeCSVImportView,
    EmployeeCSVExportView,
    EmployeeProfilePDFView,
    EmployeeSalarySlipPDFView,
    EmployeeIDCardPDFView,

    # Departments
    DepartmentListCreateView,
    DepartmentDetailView,
    DepartmentEmployeesView,

    # Audit Logs
    AuditLogListView,
    
    # Dashboard & Reports
    DashboardView,
    ReportView,
    ReportDownloadView,
)

app_name = "v1"

urlpatterns = [
    # ───────────────── Authentication ─────────────────
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),

    # ───────────────── Employees ─────────────────────
    path(
        "employees/",
        EmployeeListCreateView.as_view(),
        name="employee-list-create",
    ),
    path(
        "employees/<int:pk>/",
        EmployeeDetailView.as_view(),
        name="employee-detail",
    ),
    path(
        "employees/import/",
        EmployeeImportView.as_view(),
        name="employee-import",
    ),
    path(
        "employees/export/",
        EmployeeExportView.as_view(),
        name="employee-export",
    ),
    path(
        "employees/csv/import/",
        EmployeeCSVImportView.as_view(),
        name="employee-csv-import",
    ),
    path(
        "employees/csv/export/",
        EmployeeCSVExportView.as_view(),
        name="employee-csv-export",
    ),
    path(
        "employees/<int:pk>/pdf-profile/",
        EmployeeProfilePDFView.as_view(),
        name="employee-pdf-profile",
    ),
    path(
        "employees/<int:pk>/salary-slip/",
        EmployeeSalarySlipPDFView.as_view(),
        name="employee-salary-slip",
    ),
    path(
        "employees/<int:pk>/id-card/",
        EmployeeIDCardPDFView.as_view(),
        name="employee-id-card",
    ),

    # ───────────────── Departments ───────────────────
    path(
        "departments/",
        DepartmentListCreateView.as_view(),
        name="department-list-create",
    ),
    path(
        "departments/<int:pk>/",
        DepartmentDetailView.as_view(),
        name="department-detail",
    ),
    path(
        "departments/<int:pk>/employees/",
        DepartmentEmployeesView.as_view(),
        name="department-employees",
    ),

    # ───────────────── Audit Logs ────────────────────
    path(
        "audit-logs/",
        AuditLogListView.as_view(),
        name="audit-log-list",
    ),

    # ───────────────── Dashboard & Reports ──────────────
    path(
        "dashboard/",
        DashboardView.as_view(),
        name="dashboard",
    ),
    path(
        "reports/",
        ReportView.as_view(),
        name="reports",
    ),
    path(
        "reports/<str:pk>/download/",
        ReportDownloadView.as_view(),
        name="report-download",
    ),
]