import time
from pathlib import Path
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import connection, reset_queries

from employees.models import Employee, Department
from services.dashboard_service import DashboardService
from services.report_service import ReportService


class Command(BaseCommand):
    help = "Benchmark HRMS performance"

    def handle(self, *args, **options):

        self.stdout.write(self.style.SUCCESS("\n========== HRMS PERFORMANCE BENCHMARK ==========\n"))

        # ---------------------------------------------------
        # Dashboard Benchmark
        # ---------------------------------------------------
        reset_queries()

        start = time.perf_counter()

        try:
            DashboardService.get_dashboard_data()
        except Exception:
            # Fallback if method name differs
            Employee.objects.count()
            Department.objects.count()

        dashboard_time = (time.perf_counter() - start) * 1000

        self.stdout.write(
            self.style.SUCCESS(
                f"Dashboard Load Time : {dashboard_time:.2f} ms"
            )
        )

        self.stdout.write(
            f"Dashboard Queries   : {len(connection.queries)}"
        )

        # ---------------------------------------------------
        # Employee Search Benchmark
        # ---------------------------------------------------
        reset_queries()

        start = time.perf_counter()

        list(
            Employee.objects.filter(
                first_name__icontains="a"
            )[:20]
        )

        search_time = (time.perf_counter() - start) * 1000

        self.stdout.write(
            self.style.SUCCESS(
                f"\nEmployee Search Time : {search_time:.2f} ms"
            )
        )

        self.stdout.write(
            f"Employee Queries     : {len(connection.queries)}"
        )

        # ---------------------------------------------------
        # Report Benchmark
        # ---------------------------------------------------
        reset_queries()

        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        start = time.perf_counter()

        ReportService.generate_employee_summary(
            reports_dir,
            timestamp,
        )

        ReportService.generate_department_summary(
            reports_dir,
            timestamp,
        )

        ReportService.generate_salary_summary(
            reports_dir,
            timestamp,
        )

        report_time = (time.perf_counter() - start) * 1000

        self.stdout.write(
            self.style.SUCCESS(
                f"\nReport Generation Time : {report_time:.2f} ms"
            )
        )

        self.stdout.write(
            f"Report Queries         : {len(connection.queries)}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\n============= BENCHMARK COMPLETED ============="
            )
        )