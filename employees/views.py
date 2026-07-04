from django.contrib import messages
from django.core.cache import cache
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
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)


from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Employee, Department, Attendance, Payroll
from .forms import EmployeeForm

from services.dashboard_service import DashboardService
from services.employee_service import EmployeeService


# ══════════════════════════════════════════════════════════════
# Static Pages
# ══════════════════════════════════════════════════════════════

def home(request):
    return render(request, "employees/home.html")


def about(request):
    return render(request, "employees/about.html")


def contact(request):
    return render(request, "employees/contact.html")


# ══════════════════════════════════════════════════════════════
# Session Management
# ══════════════════════════════════════════════════════════════

def clear_session(request):
    """
    Clear the entire session (logout helper).
    Prevents session fixation by calling flush().
    """
    request.session.flush()
    messages.success(request, "Session cleared successfully.")
    return redirect("home")


def _store_search_in_session(request):
    """
    Store the current search/filter parameters in the session
    so the user returns to their previous filter state.
    """
    request.session["last_search"] = {
        "search": request.GET.get("search", ""),
        "department": request.GET.get("department", ""),
        "status": request.GET.get("status", ""),
        "email": request.GET.get("email", ""),
        "min_salary": request.GET.get("min_salary", ""),
        "max_salary": request.GET.get("max_salary", ""),
    }


def _store_dashboard_preferences(request):
    """
    Store dashboard visit metadata in the session.
    """
    if hasattr(request, "user") and request.user.is_authenticated:
        request.session["dashboard_preferences"] = {
            "user_role": getattr(request.user, "role", ""),
            "last_visited": timezone.now().isoformat(),
        }
    request.session["selected_department"] = request.GET.get("department", "")


# ══════════════════════════════════════════════════════════════
# Employee List + Search + Filter + Pagination (20/page)
# ══════════════════════════════════════════════════════════════

class EmployeeListView(ListView):
    """
    Paginated employee list with advanced search.
    Delegates to EmployeeService for optimized queries.
    Stores search params in session for state persistence.
    """
    model = Employee
    template_name = "employees/employees.html"
    context_object_name = "employees"
    paginate_by = 20  # Module 6: 20 records per page

    def get_queryset(self):
        # Store search parameters in session
        _store_search_in_session(self.request)

        search = self.request.GET.get("search")
        department = self.request.GET.get("department")
        status = self.request.GET.get("status")
        email = self.request.GET.get("email")
        min_salary = self.request.GET.get("min_salary")
        max_salary = self.request.GET.get("max_salary")
        exclude_inactive = self.request.GET.get("exclude_inactive")

        # Use EmployeeService for optimized base queryset
        queryset = EmployeeService.list_employees()

        # Advanced search — case-insensitive, partial matching
        if search:
            queryset = queryset.filter(
                Q(employee_id__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(department__name__icontains=search)
            )

        # Email-specific filter
        if email:
            queryset = queryset.filter(email__icontains=email)

        # Department filter
        if department:
            queryset = queryset.filter(department__name__icontains=department)

        # Salary range filters
        if min_salary:
            queryset = queryset.filter(salary__gte=min_salary)
        if max_salary:
            queryset = queryset.filter(salary__lte=max_salary)

        # Status filter
        if exclude_inactive == "true":
            queryset = queryset.filter(~Q(status=False))
        else:
            if status == "active":
                queryset = queryset.filter(status=True)
            elif status == "inactive":
                queryset = queryset.filter(status=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass departments for the filter dropdown
        context["departments"] = Department.objects.order_by("name").values_list("name", flat=True)
        return context


# ══════════════════════════════════════════════════════════════
# Employee CRUD
# ══════════════════════════════════════════════════════════════

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
        response = super().form_valid(form)
        # Invalidate caches after creating employee
        DashboardService.invalidate_dashboard_cache()
        cache.delete("employee_statistics")
        cache.delete("department_statistics")
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Validation Failed"
        )
        return super().form_invalid(form)


class EmployeeDetailView(DetailView):
    """
    Employee detail with optimized queries.
    Uses select_related and prefetch_related to avoid N+1.
    """
    model = Employee
    template_name = "employees/detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        return (
            Employee.objects
            .select_related("department", "manager", "profile")
            .prefetch_related("skills")
        )


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
        response = super().form_valid(form)
        # Invalidate caches after updating employee
        DashboardService.invalidate_dashboard_cache()
        cache.delete("employee_statistics")
        cache.delete("department_statistics")
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Validation Failed"
        )
        return super().form_invalid(form)


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
        response = super().form_valid(form)
        # Invalidate caches after deleting employee
        DashboardService.invalidate_dashboard_cache()
        cache.delete("employee_statistics")
        cache.delete("department_statistics")
        return response


# ══════════════════════════════════════════════════════════════
# Analytics Dashboard (Optimized — max 5 queries, cached 2 min)
# ══════════════════════════════════════════════════════════════

@cache_page(120)  # Cache entire response for 2 minutes
def analytics_dashboard(request):
    """
    Optimized dashboard using DashboardService.
    Displays all 7 KPIs with maximum 5 database queries.
    Dashboard data is also cached at the service layer.
    """
    # Store dashboard preferences in session
    _store_dashboard_preferences(request)

    # Delegate to service layer — returns cached data
    context = DashboardService.get_dashboard_data()

    return render(
        request,
        "employees/analytics_dashboard.html",
        context,
    )


# ══════════════════════════════════════════════════════════════
# Department List (Cached 30 min, 10/page)
# ══════════════════════════════════════════════════════════════

@method_decorator(cache_page(1800), name="dispatch")  # 30 minutes
class DepartmentListView(ListView):
    """
    Department list with employee count annotations.
    Cached at HTTP level for 30 minutes.
    """
    model = Department
    template_name = "employees/department_list.html"
    context_object_name = "departments"
    paginate_by = 10  # Module 6: 10 records per page

    def get_queryset(self):
        return (
            Department.objects
            .annotate(
                employee_count=Count("employee_set"),
                average_salary=Avg("employee_set__salary"),
                highest_salary=Max("employee_set__salary"),
                lowest_salary=Min("employee_set__salary"),
            )
            .order_by("name")
        )


# ══════════════════════════════════════════════════════════════
# Attendance List (50/page, with search)
# ══════════════════════════════════════════════════════════════

class AttendanceListView(ListView):
    """
    Attendance records with search and pagination (50/page).
    Uses select_related to avoid N+1 queries on employee/department.
    """
    model = Attendance
    template_name = "employees/attendance_list.html"
    context_object_name = "attendance_records"
    paginate_by = 50  # Module 6: 50 records per page

    def get_queryset(self):
        employee_name = self.request.GET.get("employee_name")
        status = self.request.GET.get("status")
        date = self.request.GET.get("date")

        # Delegate to service for optimized query
        return EmployeeService.search_attendance(
            employee_name=employee_name,
            status=status,
            date=date,
        )


# ══════════════════════════════════════════════════════════════
# HR Reports (Cached 10 min)
# ══════════════════════════════════════════════════════════════

@cache_page(600)  # Cache entire response for 10 minutes
def hr_reports(request):
    """
    HR Reports page displaying cached statistics.
    Uses low-level cache from EmployeeService.
    """
    context = {
        "employee_stats": EmployeeService.employee_statistics(),
        "department_stats": EmployeeService.department_salary_statistics(),
        "payroll_summary": EmployeeService.payroll_summary(),
    }
    return render(request, "employees/hr_reports.html", context)


# ══════════════════════════════════════════════════════════════
# Salary Operations (Delegated to Service)
# ══════════════════════════════════════════════════════════════

def increase_salary(request):
    EmployeeService.increase_salary_by_10_percent()

    # Invalidate caches
    DashboardService.invalidate_dashboard_cache()
    cache.delete("employee_statistics")
    cache.delete("department_statistics")

    messages.success(
        request,
        "All employee salaries increased by 10%."
    )

    return redirect("analytics_dashboard")


def process_payroll(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    try:
        EmployeeService.process_payroll(employee, employee.salary)

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