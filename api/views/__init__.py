from .employee_views import (
    EmployeeListCreateView,
    EmployeeDetailView,
    EmployeeAnalyticsView,
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

__all__ = [

    # Employee Views (V1)
    "EmployeeListCreateView",
    "EmployeeDetailView",
    "EmployeeAnalyticsView",

    # Department Views
    "DepartmentListCreateView",
    "DepartmentDetailView",
    "DepartmentEmployeesView",

    # Authentication
    "LoginView",
    "TokenRefreshView",
    "LogoutView",

    # Audit Logs
    "AuditLogListView",

    # V2
    "EmployeeV2ListCreateView",
    "EmployeeV2DetailView",
]