from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .class_views import EmployeeListAPIView, EmployeeDetailAPIView
from .generic_views import (
    EmployeeListCreateAPIView,
    EmployeeRetrieveUpdateDestroyAPIView,
)
from .viewsets import EmployeeViewSet

router = DefaultRouter()
router.register(r'viewset/employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    # Function-Based Views
    path("employees/", views.employee_list, name="employee-list"),
    path("employees/<int:pk>/", views.employee_detail, name="employee-detail"),

    # Class-Based Views
    path(
        "cbv/employees/",
        EmployeeListAPIView.as_view(),
        name="cbv-employee-list",
    ),
    path(
        "cbv/employees/<int:pk>/",
        EmployeeDetailAPIView.as_view(),
        name="cbv-employee-detail",
    ),

    # Generic Views
    path(
        "generic/employees/",
        EmployeeListCreateAPIView.as_view(),
        name="generic-employee-list-create",
    ),
    path(
        "generic/employees/<int:pk>/",
        EmployeeRetrieveUpdateDestroyAPIView.as_view(),
        name="generic-employee-detail",
    ),

    # ViewSets
    path("", include(router.urls)),
]