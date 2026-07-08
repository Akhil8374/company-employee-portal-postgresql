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
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)

from .audit_log_views import AuditLogListView

from .v2_employee_views import (
    EmployeeV2ListCreateView,
    EmployeeV2DetailView,
)

from .profile_views import (
    MyProfileView,
    ProfileImageUploadView,
)

from .dashboard_views import (
    DashboardView,
    ReportView,
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
    "ChangePasswordView",
    "ForgotPasswordView",
    "ResetPasswordView",

    # Audit Logs
    "AuditLogListView",

    # Employee V2
    "EmployeeV2ListCreateView",
    "EmployeeV2DetailView",

    # Profile & Image Upload
    "MyProfileView",
    "ProfileImageUploadView",

    # Dashboard & Reports
    "DashboardView",
    "ReportView",
]