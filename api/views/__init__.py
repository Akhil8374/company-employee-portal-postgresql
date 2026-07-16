from .employee_views import (
    EmployeeListCreateView,
    EmployeeDetailView,
    EmployeeImportView,
    EmployeeExportView,
    EmployeeCSVImportView,
    EmployeeCSVExportView,
    EmployeeProfilePDFView,
    EmployeeSalarySlipPDFView,
    EmployeeIDCardPDFView,
)

from .department_views import (
    DepartmentListCreateView,
    DepartmentDetailView,
    DepartmentEmployeesView,
)

from .auth_views import (
    LoginView,
    TokenRefreshView,
    LogoutView,
)

from .audit_log_views import AuditLogListView

from .v2_employee_views import (
    EmployeeV2ListCreateView,
    EmployeeV2DetailView,
)

from .dashboard_views import (
    DashboardView,
    ReportView,
    ReportDownloadView,
    StoredReportDownloadView,
    DashboardExportView,
    EmployeeQRCodeView,
)

__all__ = [
    "EmployeeListCreateView",
    "EmployeeDetailView",
    "EmployeeImportView",
    "EmployeeExportView",
    "EmployeeCSVImportView",
    "EmployeeCSVExportView",
    "EmployeeProfilePDFView",
    "EmployeeSalarySlipPDFView",
    "EmployeeIDCardPDFView",

    "DepartmentListCreateView",
    "DepartmentDetailView",
    "DepartmentEmployeesView",

    "LoginView",
    "TokenRefreshView",
    "LogoutView",

    "AuditLogListView",

    "EmployeeV2ListCreateView",
    "EmployeeV2DetailView",

    "DashboardView",
    "ReportView",
    "ReportDownloadView",
    "StoredReportDownloadView",
    "DashboardExportView",
    "EmployeeQRCodeView",
]