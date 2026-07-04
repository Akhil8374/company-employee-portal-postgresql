from django.contrib import messages
from django.db import transaction
from django.db.models import (
    Q,
    Count,
    Sum,
    Avg,
    Max,
    Min,
    F,

)
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,)


from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Employee,Payroll
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
        queryset = (
    Employee.objects
    .select_related("department", "manager")
    .prefetch_related("skills")
    .only(
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "salary",
        "designation",
        "status",
        "department",
        "manager",
    )
    .order_by("employee_id")
)

        search = self.request.GET.get("search")
        department = self.request.GET.get("department")
        status = self.request.GET.get("status")
        min_salary = self.request.GET.get("min_salary")
        exclude_inactive = self.request.GET.get("exclude_inactive")

        if search:
            queryset = queryset.filter(
                Q(employee_id__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(department__name__icontains=search)
            )

        if department and min_salary:
            # Explicit Q() & Q() AND condition
            queryset = queryset.filter(
                Q(department__name=department) & Q(salary__gte=min_salary)
            )
        elif department:
            queryset = queryset.filter(
                department__name=department
            )

        if exclude_inactive == "true":
            # Explicit ~Q() NOT condition
            queryset = queryset.filter(~Q(status=False))
        else:
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
    
      
def analytics_dashboard(request):
    # defer() optimization
    top_employees = Employee.objects.defer("created_at", "updated_at", "profile_image").order_by("-salary")[:10]
    
    department_report = (
        Employee.objects
        .values("department__name")
        .annotate(
            employee_count=Count("id"),
            average_salary=Avg("salary"),
            highest_salary=Max("salary"),
            lowest_salary=Min("salary"),
        )
        .order_by("department__name")
    )

    salary_statistics = Employee.objects.aggregate(
        total_salary=Sum("salary"),
        average_salary=Avg("salary"),
        highest_salary=Max("salary"),
        lowest_salary=Min("salary"),
    )

    joined_this_month = Employee.objects.filter(
        joining_date__month=timezone.now().month,
        joining_date__year=timezone.now().year,
    )

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status=True).count()
    inactive_employees = Employee.objects.filter(status=False).count()
    joined_today = Employee.objects.filter(joining_date=timezone.now().date()).count()

    context = {
        "top_employees": top_employees,
        "department_report": department_report,
        "salary_statistics": salary_statistics,
        "joined_this_month": joined_this_month,
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,
        "joined_today": joined_today,
    }
    return render(
        request,
        "employees/analytics_dashboard.html",
     context,
    )

def increase_salary(request):

    Employee.objects.update(
        salary=F("salary") * 1.10
    )

    messages.success(
        request,
        "All employee salaries increased by 10%."
    )

    return redirect("analytics_dashboard")


def process_payroll(request, employee_id):

    employee = Employee.objects.get(id=employee_id)

    try:
        with transaction.atomic():

            Payroll.objects.create(
                employee=employee,
                amount=employee.salary,
                status="SUCCESS",
            )

    except Exception:

        messages.error(
            request,
            "Payroll processing failed."
        )

    else:

        messages.success(
            request,
            "Payroll processed successfully."
        )

    return redirect("employees")