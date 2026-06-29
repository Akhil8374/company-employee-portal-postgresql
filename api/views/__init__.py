from .employee_views import EmployeeListCreateView, EmployeeDetailView
from .department_views import (
    DepartmentListCreateView,
    DepartmentDetailView,
    DepartmentEmployeesView,
)
from .auth_views import LoginView, TokenRefreshView, LogoutView
from .audit_log_views import AuditLogListView
from .v2_employee_views import EmployeeV2ListCreateView, EmployeeV2DetailView

__all__ = [
    # Employee Views (V1)
    "EmployeeListCreateView",
    "EmployeeDetailView",
    # Department Views
    "DepartmentListCreateView",
    "DepartmentDetailView",
    "DepartmentEmployeesView",
    # Auth Views
    "LoginView",
    "TokenRefreshView",
    "LogoutView",
    # Audit Log Views
    "AuditLogListView",
    # V2 Views
    "EmployeeV2ListCreateView",
    "EmployeeV2DetailView",
]
