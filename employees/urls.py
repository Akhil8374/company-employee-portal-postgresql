from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

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
]