from django.core.cache import cache
from django.db.models import (
    Count,
    Avg,
    Max,
    Min,
    Q,
)
from django.utils import timezone
from employees.models import Employee, Department, Attendance


class DashboardService:
    """
    Service class for Analytics Dashboard queries.
    Optimizes queries to run in maximum 5 database operations.
    Results are cached for 2 minutes (120 seconds).
    """

    CACHE_KEY = "dashboard_data"
    CACHE_TIMEOUT = 120  # 2 minutes

    @staticmethod
    def get_dashboard_data():
        """
        Return all dashboard KPIs. Uses low-level cache to avoid
        hitting the database on every request.
        """
        data = cache.get(DashboardService.CACHE_KEY)
        if data is not None:
            return data

        today = timezone.now().date()
        current_year = timezone.now().year
        current_month = timezone.now().month

        # Query 1: Aggregate stats on Employee (total, active, new joiners, average salary)
        employee_stats = Employee.objects.aggregate(
            total_employees=Count("id"),
            active_employees=Count("id", filter=Q(status=True)),
            new_joiners=Count("id", filter=Q(joining_date__year=current_year, joining_date__month=current_month)),
            average_salary=Avg("salary"),
        )

        # Query 2: Department Count
        department_count = Department.objects.count()

        # Query 3: Employees on Leave today
        employees_on_leave = Attendance.objects.filter(
            date=today,
            status="LEAVE",
        ).count()

        # Query 4: Top 10 highest paid employees
        top_employees = list(
            Employee.objects
            .select_related("department")
            .order_by("-salary")[:10]
        )

        # Query 5: Department Report with statistics
        department_report = list(
            Department.objects.annotate(
                employee_count=Count("employee_set"),
                average_salary=Avg("employee_set__salary"),
                highest_salary=Max("employee_set__salary"),
                lowest_salary=Min("employee_set__salary"),
            ).order_by("name")
        )

        data = {
            "total_employees": employee_stats["total_employees"] or 0,
            "active_employees": employee_stats["active_employees"] or 0,
            "new_joiners": employee_stats["new_joiners"] or 0,
            "average_salary": employee_stats["average_salary"] or 0,
            "total_departments": department_count,
            "department_count": department_count,
            "employees_on_leave": employees_on_leave,
            "top_employees": top_employees,
            "department_report": department_report,
        }

        cache.set(DashboardService.CACHE_KEY, data, timeout=DashboardService.CACHE_TIMEOUT)
        return data

    @staticmethod
    def invalidate_dashboard_cache():
        """Clear the dashboard cache. Call after employee/attendance changes."""
        cache.delete(DashboardService.CACHE_KEY)
