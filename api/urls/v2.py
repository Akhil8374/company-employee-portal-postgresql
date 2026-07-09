from django.urls import path

from api.views import (
    EmployeeV2ListCreateView,
    EmployeeV2DetailView,
)

app_name = "v2"

urlpatterns = [
    # ── V2 Employees (Expanded: Employee + Department + Manager) ──
    path("employees/", EmployeeV2ListCreateView.as_view(), name="employee-list-create"),
    path("employees/<int:pk>/", EmployeeV2DetailView.as_view(), name="employee-detail"),
]
