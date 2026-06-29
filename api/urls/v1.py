from django.urls import path

from api.views import (
    # Auth
    LoginView,
    TokenRefreshView,
    LogoutView,
    # Employees
    EmployeeListCreateView,
    EmployeeDetailView,
    # Departments
    DepartmentListCreateView,
    DepartmentDetailView,
    DepartmentEmployeesView,
    # Audit Logs
    AuditLogListView,
)

app_name = "v1"

urlpatterns = [
    # ── Authentication ─────────────────────────────────────────
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),

    # ── Employees ──────────────────────────────────────────────
    path("employees/", EmployeeListCreateView.as_view(), name="employee-list-create"),
    path("employees/<int:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),

    # ── Departments ────────────────────────────────────────────
    path("departments/", DepartmentListCreateView.as_view(), name="department-list-create"),
    path("departments/<int:pk>/", DepartmentDetailView.as_view(), name="department-detail"),
    path(
        "departments/<int:pk>/employees/",
        DepartmentEmployeesView.as_view(),
        name="department-employees",
    ),

    # ── Audit Logs (Admin Only) ────────────────────────────────
    path("audit-logs/", AuditLogListView.as_view(), name="audit-log-list"),
]
