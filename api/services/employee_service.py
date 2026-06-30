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

from employees.models import (
    Employee,
    Department,
    Payroll,
)


class EmployeeService:
    """
    Service class for Employee ORM operations.
    """

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

    @staticmethod
    def employee_statistics():
        return Employee.objects.aggregate(
            total_employees=Count("id"),
            total_salary=Sum("salary"),
            average_salary=Avg("salary"),
            highest_salary=Max("salary"),
            lowest_salary=Min("salary"),
        )

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
    def department_salary_statistics():
        return Department.objects.annotate(
            employee_count=Count("employee_set"),
            average_salary=Avg("employee_set__salary"),
            highest_salary=Max("employee_set__salary"),
            lowest_salary=Min("employee_set__salary"),
        )

    @staticmethod
    def advanced_search():
        return Employee.objects.filter(
            Q(department__name="IT") &
            Q(salary__gt=50000)
        )

    @staticmethod
    @transaction.atomic
    def process_payroll(employee, amount):
        """
        Transaction-safe payroll processing.
        If payroll creation fails,
        everything rolls back.
        """

        employee.salary = amount
        employee.save()

        Payroll.objects.create(
            employee=employee,
            amount=amount,
            status="SUCCESS",
        )

        return True