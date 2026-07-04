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
)


class EmployeeService:
    """
    Service class for Employee ORM operations.
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
    # Cached Employee Statistics
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

            cache.set(cache_key, data, timeout=300)

        return data

    # ==========================================================
    # Cached Department Statistics
    # ==========================================================

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
                )
            )

            cache.set(cache_key, data, timeout=300)

        return data

    # ==========================================================
    # Cached Payroll Summary
    # ==========================================================

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

            cache.set(cache_key, data, timeout=300)

        return data

    # ==========================================================
    # Employee Reports
    # ==========================================================

    @staticmethod
    def top_paid_employees():
        return Employee.objects.order_by("-salary")[:10]

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
    def advanced_search():
        return Employee.objects.filter(
            Q(department__name="IT") &
            Q(salary__gt=50000)
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
            .select_related("department")
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

        if status:
            queryset = queryset.filter(
                status__iexact=status
            )

        return queryset
# ==========================================================
# Optimized Employee CRUD Queries
# ==========================================================
        # ==========================================================
    # Optimized Employee CRUD Queries
    # ==========================================================

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
        # ==========================================================
    # Dashboard Summary
    # ==========================================================

    @staticmethod
    def dashboard_summary():

        return {
            "total_employees": Employee.objects.count(),
            "total_departments": Department.objects.count(),
            "active_employees": Employee.objects.filter(status="Active").count(),
            "new_joiners": Employee.objects.filter(
                joining_date__year=timezone.now().year,
                joining_date__month=timezone.now().month,
            ).count(),
            "average_salary": Employee.objects.aggregate(
                average=Avg("salary")
            )["average"],
        }   
    # ==========================================================
    # Payroll Transaction
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

        # Clear payroll cache after update
        cache.delete("payroll_summary")

        return True