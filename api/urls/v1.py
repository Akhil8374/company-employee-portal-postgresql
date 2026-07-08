from django.urls import path

from api.views import (

    # ── Authentication (Module 1–4) ───────────────────────────────────────────
    LoginView,
    TokenRefreshView,
    LogoutView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,

    # ── Profile & Image Upload (Module 6 + 8) ────────────────────────────────
    MyProfileView,
    ProfileImageUploadView,

    # ── Employees (Module 5 + 7) ─────────────────────────────────────────────
    EmployeeListCreateView,
    EmployeeDetailView,
    EmployeeAnalyticsView,

    # ── Departments ──────────────────────────────────────────────────────────
    DepartmentListCreateView,
    DepartmentDetailView,
    DepartmentEmployeesView,

    # ── Dashboard & Reports (Module 12) ──────────────────────────────────────
    DashboardView,
    ReportView,

    # ── Audit Logs ───────────────────────────────────────────────────────────
    AuditLogListView,
)

app_name = "v1"

urlpatterns = [

    # ══════════════════════════════════════════════════════════════════════════
    # AUTHENTICATION  (Modules 1–4)
    # ══════════════════════════════════════════════════════════════════════════

    # Module 1: Login — returns JWT access + refresh tokens
    path(
        "auth/login/",
        LoginView.as_view(),
        name="login",
    ),

    # Module 1: Refresh — exchange refresh token for new access token
    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    # Module 2: Logout — blacklist refresh token + flush session
    path(
        "auth/logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    # Module 3: Change Password (authenticated)
    path(
        "auth/change-password/",
        ChangePasswordView.as_view(),
        name="change-password",
    ),

    # Module 4: Forgot Password — generate reset token
    path(
        "auth/forgot-password/",
        ForgotPasswordView.as_view(),
        name="forgot-password",
    ),

    # Module 4: Reset Password — validate token + update password
    path(
        "auth/reset-password/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # PROFILE  (Modules 6 + 8 — Object-Level Permission + Secure Upload)
    # ══════════════════════════════════════════════════════════════════════════

    # Module 6: Own profile (GET/PUT — authenticated user only)
    path(
        "profile/",
        MyProfileView.as_view(),
        name="my-profile",
    ),

    # Module 8: Profile image upload (secure file validation)
    path(
        "profile/image/",
        ProfileImageUploadView.as_view(),
        name="profile-image-upload",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # EMPLOYEES  (Modules 5 + 7 + 9 — Role-Based Access, Throttling, Validation)
    # ══════════════════════════════════════════════════════════════════════════

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
        "employees/analytics/",
        EmployeeAnalyticsView.as_view(),
        name="employee-analytics",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # DEPARTMENTS
    # ══════════════════════════════════════════════════════════════════════════

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

    # ══════════════════════════════════════════════════════════════════════════
    # DASHBOARD & REPORTS  (Module 12)
    # ══════════════════════════════════════════════════════════════════════════

    # Dashboard — Admin, HR, Manager only
    path(
        "dashboard/",
        DashboardView.as_view(),
        name="dashboard",
    ),

    # Reports — Admin only (strict throttle: 20/min)
    path(
        "reports/",
        ReportView.as_view(),
        name="reports",
    ),

    # ══════════════════════════════════════════════════════════════════════════
    # AUDIT LOGS  (Module 10)
    # ══════════════════════════════════════════════════════════════════════════

    path(
        "audit-logs/",
        AuditLogListView.as_view(),
        name="audit-log-list",
    ),
]