import os
from datetime import datetime

from django.db.models import Count, Sum, Avg, Max, Min

from employees.models import Employee, Department


class ReportService:
    """
    Service class for generating employee, department,
    and salary reports.
    """

    @staticmethod
    def generate_employee_summary(reports_dir, timestamp):
        total = Employee.objects.count()
        active = Employee.objects.filter(status=True).count()
        inactive = Employee.objects.filter(status=False).count()

        filepath = os.path.join(
            reports_dir,
            f"employee_summary_{timestamp}.txt",
        )

        with open(filepath, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("EMPLOYEE SUMMARY REPORT\n")
            f.write(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("=" * 50 + "\n\n")

            f.write(f"Total Employees   : {total}\n")
            f.write(f"Active Employees  : {active}\n")
            f.write(f"Inactive Employees: {inactive}\n\n")

            f.write("-" * 50 + "\n")
            f.write(f"{'Employee ID':<15} {'Name':<25} {'Status':<10}\n")
            f.write("-" * 50 + "\n")

            employees = (
                Employee.objects
                .select_related("department")
                .only(
                    "employee_id",
                    "first_name",
                    "last_name",
                    "status",
                    "department",
                )
                .all()
            )

            for emp in employees:
                status = "Active" if emp.status else "Inactive"
                f.write(
                    f"{emp.employee_id:<15} "
                    f"{emp.first_name} "
                    f"{emp.last_name:<20} "
                    f"{status:<10}\n"
                )

        return filepath

    @staticmethod
    def generate_department_summary(reports_dir, timestamp):
        departments = (
            Department.objects
            .annotate(
                employee_count=Count("employee_set")
            )
            .order_by("name")
        )

        filepath = os.path.join(
            reports_dir,
            f"department_summary_{timestamp}.txt",
        )

        with open(filepath, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("DEPARTMENT SUMMARY REPORT\n")
            f.write(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("=" * 50 + "\n\n")

            f.write(f"{'Department':<25} {'Employee Count':<15}\n")
            f.write("-" * 40 + "\n")

            for dept in departments:
                f.write(
                    f"{dept.name:<25} "
                    f"{dept.employee_count:<15}\n"
                )

        return filepath

    @staticmethod
    def generate_salary_summary(reports_dir, timestamp):
        stats = Employee.objects.aggregate(
            total_salary=Sum("salary"),
            average_salary=Avg("salary"),
            highest_salary=Max("salary"),
            lowest_salary=Min("salary"),
        )

        filepath = os.path.join(
            reports_dir,
            f"salary_summary_{timestamp}.txt",
        )

        with open(filepath, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("SALARY SUMMARY REPORT\n")
            f.write(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write("=" * 50 + "\n\n")

            f.write(
                f"Total Salary Expense : {stats['total_salary'] or 0:>15,.2f}\n"
            )
            f.write(
                f"Average Salary       : {stats['average_salary'] or 0:>15,.2f}\n"
            )
            f.write(
                f"Highest Salary       : {stats['highest_salary'] or 0:>15,.2f}\n"
            )
            f.write(
                f"Lowest Salary        : {stats['lowest_salary'] or 0:>15,.2f}\n\n"
            )

            f.write("-" * 60 + "\n")
            f.write("TOP 10 HIGHEST PAID EMPLOYEES\n")
            f.write("-" * 60 + "\n")
            f.write(
                f"{'Employee ID':<15} {'Name':<25} {'Salary':>15}\n"
            )
            f.write("-" * 60 + "\n")

            employees = (
                Employee.objects
                .select_related("department")
                .only(
                    "employee_id",
                    "first_name",
                    "last_name",
                    "salary",
                    "department",
                )
                .order_by("-salary")[:10]
            )

            for emp in employees:
                f.write(
                    f"{emp.employee_id:<15} "
                    f"{emp.first_name} "
                    f"{emp.last_name:<20} "
                    f"{emp.salary:>15,.2f}\n"
                )

        return filepath