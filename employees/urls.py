from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "about/",
        views.about,
        name="about",
    ),

    path(
        "contact/",
        views.contact,
        name="contact",
    ),

    # ==========================
    # Session Management
    # ==========================
    path(
        "session/clear/",
        views.clear_session,
        name="clear_session",
    ),

    # ==========================
    # Employee CRUD
    # ==========================
    path(
        "employees/",
        views.EmployeeListView.as_view(),
        name="employees",
    ),

    path(
        "employees/create/",
        views.EmployeeCreateView.as_view(),
        name="create_employee",
    ),

    path(
        "employees/<int:pk>/",
        views.EmployeeDetailView.as_view(),
        name="employee_detail",
    ),

    path(
        "employees/update/<int:pk>/",
        views.EmployeeUpdateView.as_view(),
        name="update_employee",
    ),

    path(
        "employees/delete/<int:pk>/",
        views.EmployeeDeleteView.as_view(),
        name="delete_employee",
    ),

    # ==========================
    # Analytics Dashboard
    # ==========================
    path(
        "analytics/",
        views.analytics_dashboard,
        name="analytics_dashboard",
    ),

    # ==========================
    # Department List
    # ==========================
    path(
        "departments/",
        views.DepartmentListView.as_view(),
        name="departments",
    ),

    # ==========================
    # Attendance List
    # ==========================
    path(
        "attendance/",
        views.AttendanceListView.as_view(),
        name="attendance",
    ),

    # ==========================
    # HR Reports
    # ==========================
    path(
        "reports/",
        views.hr_reports,
        name="hr_reports",
    ),
]