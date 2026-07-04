from django.db import transaction
from django.db.models import (
    F,
    Q,
    Count,
    Sum,
    Avg,
    Max,
    Min,
)
from django.utils import timezone
from django.core.cache import cache

from employees.models import (
    Employee,
    Department,
    Payroll,
    Attendance,
)


class EmployeeService:
    """
    Central service class for Employee and Attendance ORM operations.
    """

    # ==========================================================
    # Salary Operations
    # ==========================================================

    @staticmethod
    def increase_salary_by_10_percent():
        return Employee.objects.update(
            salary=F("salary") * 1.10
        )

    @staticmethod
    def increase_salary_fixed(amount):
        return Employee.objects.update(
            salary=F("salary") + amount
        )

    @staticmethod
    def increase_it_employee_salary():
        return Employee.objects.filter(
            department__name="IT"
        ).update(
            salary=F("salary") * 1.10
        )

    @staticmethod
    def increase_low_salary():
        return Employee.objects.filter(
            salary__lt=50000
        ).update(
            salary=F("salary") + 5000
        )

    # ==========================================================
    # Cached Statistics (Low-Level Cache API)
    # ==========================================================

    @staticmethod
    def employee_statistics():
        cache_key = "employee_statistics"
        data = cache.get(cache_key)
        if data is None:
            data = Employee.objects.aggregate(
                total_employees=Count("id"),
                total_salary=Sum("salary"),
                average_salary=Avg("salary"),
                highest_salary=Max("salary"),
                lowest_salary=Min("salary"),
            )
            # Cache for 10 minutes (600 seconds)
            cache.set(cache_key, data, timeout=600)
        return data

    @staticmethod
    def department_salary_statistics():
        cache_key = "department_statistics"
        data = cache.get(cache_key)
        if data is None:
            data = list(
                Department.objects.annotate(
                    employee_count=Count("employee_set"),
                    average_salary=Avg("employee_set__salary"),
                    highest_salary=Max("employee_set__salary"),
                    lowest_salary=Min("employee_set__salary"),
                ).values(
                    "name",
                    "employee_count",
                    "average_salary",
                    "highest_salary",
                    "lowest_salary",
                )
            )
            # Cache for 30 minutes (1800 seconds)
            cache.set(cache_key, data, timeout=1800)
        return data

    @staticmethod
    def payroll_summary():
        cache_key = "payroll_summary"
        data = cache.get(cache_key)
        if data is None:
            data = Payroll.objects.aggregate(
                total_payroll=Sum("amount"),
                average_payroll=Avg("amount"),
                highest_payroll=Max("amount"),
                lowest_payroll=Min("amount"),
                payroll_count=Count("id"),
            )
            # Cache for 10 minutes (600 seconds)
            cache.set(cache_key, data, timeout=600)
        return data

    # ==========================================================
    # Employee Queries
    # ==========================================================

    @staticmethod
    def top_paid_employees():
        return Employee.objects.select_related("department").order_by("-salary")[:10]

    @staticmethod
    def joined_this_month():
        today = timezone.now()
        return Employee.objects.filter(
            joining_date__year=today.year,
            joining_date__month=today.month,
        )

    @staticmethod
    def department_employee_count():
        return Department.objects.annotate(
            employee_count=Count("employee_set")
        )

    @staticmethod
    def search_employees(
        name=None,
        employee_id=None,
        department=None,
        email=None,
        status=None,
    ):
        queryset = (
            Employee.objects
            .select_related("department", "manager")
            .prefetch_related("skills")
            .all()
        )

        if name:
            queryset = queryset.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name)
            )

        if employee_id:
            queryset = queryset.filter(
                employee_id__icontains=employee_id
            )

        if department:
            queryset = queryset.filter(
                department__name__icontains=department
            )

        if email:
            queryset = queryset.filter(
                email__icontains=email
            )

        if status is not None and status != "":
            # Convert status string to boolean safely
            if isinstance(status, str):
                is_active = status.lower() in ["active", "true", "1"]
            else:
                is_active = bool(status)
            queryset = queryset.filter(status=is_active)

        return queryset

    @staticmethod
    def list_employees():
        return (
            Employee.objects
            .select_related("department", "manager")
            .prefetch_related("skills")
            .only(
                "id",
                "employee_id",
                "first_name",
                "last_name",
                "email",
                "phone",
                "salary",
                "designation",
                "joining_date",
                "status",
                "department__name",
            )
            .order_by("employee_id")
        )

    @staticmethod
    def get_employee(pk):
        return (
            Employee.objects
            .select_related("department", "manager", "profile")
            .prefetch_related("skills")
            .get(pk=pk)
        )

    @staticmethod
    def delete_employee(pk):
        employee = Employee.objects.get(pk=pk)
        employee.delete()
        # Invalidate caches
        cache.delete("employee_statistics")
        cache.delete("department_statistics")

    # ==========================================================
    # Attendance Queries
    # ==========================================================

    @staticmethod
    def list_attendance():
        return (
            Attendance.objects
            .select_related("employee", "employee__department")
            .all()
            .order_by("-date", "employee__employee_id")
        )

    @staticmethod
    def search_attendance(
        employee_name=None,
        status=None,
        date=None,
    ):
        queryset = (
            Attendance.objects
            .select_related("employee", "employee__department")
            .all()
        )

        if employee_name:
            queryset = queryset.filter(
                Q(employee__first_name__icontains=employee_name) |
                Q(employee__last_name__icontains=employee_name)
            )

        if status:
            queryset = queryset.filter(status__iexact=status)

        if date:
            queryset = queryset.filter(date=date)

        return queryset.order_by("-date", "employee__employee_id")

    # ==========================================================
    # Payroll Transaction & Operations
    # ==========================================================

    @staticmethod
    @transaction.atomic
    def process_payroll(employee, amount):
        employee.salary = amount
        employee.save()

        Payroll.objects.create(
            employee=employee,
            amount=amount,
            status="SUCCESS",
        )

        # Clear payroll & stats cache after update
        cache.delete("payroll_summary")
        cache.delete("employee_statistics")
        cache.delete("department_statistics")
        return True
