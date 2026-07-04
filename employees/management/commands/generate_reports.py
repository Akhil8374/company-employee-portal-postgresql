import os
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum, Avg, Max, Min
from django.conf import settings

from employees.models import Employee, Department


class Command(BaseCommand):
    help = "Generate Employee, Department, and Salary summary reports and save to reports/ directory."

    def handle(self, *args, **options):
        reports_dir = os.path.join(settings.BASE_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # ── Employee Summary ──
        self._generate_employee_summary(reports_dir, timestamp)

        # ── Department Summary ──
        self._generate_department_summary(reports_dir, timestamp)

        # ── Salary Summary ──
        self._generate_salary_summary(reports_dir, timestamp)

        self.stdout.write(
            self.style.SUCCESS(f"\nAll reports saved to: {reports_dir}")
        )

    def _generate_employee_summary(self, reports_dir, timestamp):
        """Generate Employee Summary report."""
        total = Employee.objects.count()
        active = Employee.objects.filter(status=True).count()
        inactive = Employee.objects.filter(status=False).count()

        filepath = os.path.join(reports_dir, f"employee_summary_{timestamp}.txt")

        with open(filepath, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("EMPLOYEE SUMMARY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Employees   : {total}\n")
            f.write(f"Active Employees  : {active}\n")
            f.write(f"Inactive Employees: {inactive}\n\n")

            f.write("-" * 50 + "\n")
            f.write(f"{'Employee ID':<15} {'Name':<25} {'Status':<10}\n")
            f.write("-" * 50 + "\n")

            for emp in Employee.objects.select_related("department").all():
                status = "Active" if emp.status else "Inactive"
                f.write(f"{emp.employee_id:<15} {emp.first_name} {emp.last_name:<20} {status:<10}\n")

        self.stdout.write(self.style.SUCCESS(f"  [OK] Employee Summary: {filepath}"))

    def _generate_department_summary(self, reports_dir, timestamp):
        """Generate Department Summary report."""
        departments = (
            Department.objects
            .annotate(employee_count=Count("employee_set"))
            .order_by("name")
        )

        filepath = os.path.join(reports_dir, f"department_summary_{timestamp}.txt")

        with open(filepath, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("DEPARTMENT SUMMARY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"{'Department':<25} {'Employee Count':<15}\n")
            f.write("-" * 40 + "\n")

            for dept in departments:
                f.write(f"{dept.name:<25} {dept.employee_count:<15}\n")

        self.stdout.write(self.style.SUCCESS(f"  [OK] Department Summary: {filepath}"))

    def _generate_salary_summary(self, reports_dir, timestamp):
        """Generate Salary Summary report."""
        stats = Employee.objects.aggregate(
            total_salary=Sum("salary"),
            average_salary=Avg("salary"),
            highest_salary=Max("salary"),
            lowest_salary=Min("salary"),
        )

        filepath = os.path.join(reports_dir, f"salary_summary_{timestamp}.txt")

        with open(filepath, "w") as f:
            f.write("=" * 50 + "\n")
            f.write("SALARY SUMMARY REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Salary Expense : {stats['total_salary'] or 0:>15,.2f}\n")
            f.write(f"Average Salary       : {stats['average_salary'] or 0:>15,.2f}\n")
            f.write(f"Highest Salary       : {stats['highest_salary'] or 0:>15,.2f}\n")
            f.write(f"Lowest Salary        : {stats['lowest_salary'] or 0:>15,.2f}\n\n")

            # Top 10 highest paid
            f.write("-" * 60 + "\n")
            f.write("TOP 10 HIGHEST PAID EMPLOYEES\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Employee ID':<15} {'Name':<25} {'Salary':>15}\n")
            f.write("-" * 60 + "\n")

            for emp in Employee.objects.order_by("-salary")[:10]:
                f.write(f"{emp.employee_id:<15} {emp.first_name} {emp.last_name:<20} {emp.salary:>15,.2f}\n")

        self.stdout.write(self.style.SUCCESS(f"  [OK] Salary Summary: {filepath}"))
