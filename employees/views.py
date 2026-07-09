from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.shortcuts import render, redirect, get_object_or_404

from .models import Employee
from .forms import EmployeeForm


def home(request):
    return render(request, "employees/home.html")


def about(request):
    return render(request, "employees/about.html")


def contact(request):
    return render(request, "employees/contact.html")


# Employee List + Search + Filter + Pagination
class EmployeeListView(ListView):
    model = Employee
    template_name = "employees/employees.html"
    context_object_name = "employees"
    paginate_by = 10

    def get_queryset(self):

        queryset = Employee.objects.all().order_by("employee_id")

        search = self.request.GET.get("search")
        department = self.request.GET.get("department")
        status = self.request.GET.get("status")

        if search:
            queryset = queryset.filter(
                Q(employee_id__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(department__name__icontains=search)
            )

        if department:
            queryset = queryset.filter(
                department__name=department
            )

        if status == "active":
            queryset = queryset.filter(status=True)

        elif status == "inactive":
            queryset = queryset.filter(status=False)

        return queryset
class EmployeeCreateView(CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/create.html"
    success_url = reverse_lazy("employees")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Employee Created Successfully"
        )
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Validation Failed"
        )
        return super().form_invalid(form)
    

# Employee Detail
class EmployeeDetailView(DetailView):
    model = Employee
    template_name = "employees/detail.html"
    context_object_name = "employee"
# Update Employee
class EmployeeUpdateView(UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/update.html"
    success_url = reverse_lazy("employees")
    context_object_name = "employee"

    def form_valid(self, form):
        messages.success(
            self.request,
            "Employee Updated Successfully"
        )
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(
            self.request,
            "Validation Failed"
        )
        return super().form_invalid(form)
# Delete Employee
class EmployeeDeleteView(DeleteView):
    model = Employee
    template_name = "employees/delete.html"
    success_url = reverse_lazy("employees")
    context_object_name = "employee"

    def form_valid(self, form):
        messages.success(
            self.request,
            "Employee Deleted Successfully"
        )
        return super().form_valid(form) 
