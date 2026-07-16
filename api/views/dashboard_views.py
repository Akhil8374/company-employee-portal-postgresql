import os

from django.db.models import Count, Avg, Sum, Max, Min, Q
from django.utils import timezone
from django.http import FileResponse, Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from api.responses import SuccessResponse, ErrorResponse
from api.permissions import IsManagerOrAbove, IsAdmin, IsHROrAdmin
from api.throttling import ReportRateThrottle
from employees.models import Employee, Department, Attendance
from audit_logs.utils import create_audit_log, get_client_ip


# ─────────────────────────────────────────────────────────────────────────────
# Module 12: Dashboard API — Admin, HR, Manager only
# GET /api/v1/dashboard/
# ─────────────────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """
    Returns aggregated HRMS dashboard statistics.

    Access:   Admin | HR | Manager  (Employee role is blocked)
    Throttle: Standard (100/min)

    Data Includes:
      - Total active/inactive employees
      - Department-wise headcount
      - Average salary by department
      - Attendance summary for today
      - Recent joiners (last 30 days)
      - Salary statistics
    """
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        today = timezone.now().date()
        thirty_days_ago = today - timezone.timedelta(days=30)

        # ── Employee Summary ─────────────────────────────────────────────────
        total_employees    = Employee.objects.count()
        active_employees   = Employee.objects.filter(status=True).count()
        inactive_employees = Employee.objects.filter(status=False).count()

        # ── Department Breakdown ─────────────────────────────────────────────
        dept_stats = list(
            Department.objects.annotate(
                employee_count=Count("employee_set"),
                avg_salary=Avg("employee_set__salary"),
            ).values(
                "id", "name", "employee_count", "avg_salary"
            ).order_by("-employee_count")
        )
        # Serialize Decimals
        for dept in dept_stats:
            if dept.get("avg_salary") is not None:
                dept["avg_salary"] = round(float(dept["avg_salary"]), 2)

        # ── Attendance Today ─────────────────────────────────────────────────
        attendance_today = Attendance.objects.filter(date=today)
        attendance_summary = {
            "present":  attendance_today.filter(status="PRESENT").count(),
            "absent":   attendance_today.filter(status="ABSENT").count(),
            "leave":    attendance_today.filter(status="LEAVE").count(),
            "half_day": attendance_today.filter(status="HALF_DAY").count(),
        }

        # ── Recent Joiners (last 30 days) ────────────────────────────────────
        recent_joiners = list(
            Employee.objects.filter(
                joining_date__gte=thirty_days_ago,
                status=True,
            )
            .select_related("department")
            .values(
                "employee_id", "first_name", "last_name",
                "designation", "department__name", "joining_date",
            )
            .order_by("-joining_date")[:10]
        )
        for emp in recent_joiners:
            if emp.get("joining_date"):
                emp["joining_date"] = str(emp["joining_date"])

        # ── Salary Statistics ────────────────────────────────────────────────
        raw_stats = Employee.objects.filter(status=True).aggregate(
            total_payroll=Sum("salary"),
            average_salary=Avg("salary"),
            highest_salary=Max("salary"),
            lowest_salary=Min("salary"),
        )
        salary_stats = {
            k: round(float(v), 2) if v is not None else 0
            for k, v in raw_stats.items()
        }

        return SuccessResponse(
            data={
                "summary": {
                    "total_employees": total_employees,
                    "active_employees": active_employees,
                    "inactive_employees": inactive_employees,
                    "total_departments": Department.objects.count(),
                },
                "department_breakdown": dept_stats,
                "attendance_today": attendance_summary,
                "salary_statistics": salary_stats,
                "recent_joiners": recent_joiners,
                "generated_at": timezone.now().isoformat(),
                "accessed_by": {
                    "user": request.user.username,
                    "role": request.user.role,
                },
            },
            message="Dashboard data retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module 12: Reports API — Admin only + strict rate limiting
# GET /api/v1/reports/
# ─────────────────────────────────────────────────────────────────────────────

class ReportView(APIView):
    """
    Returns comprehensive HR reports for Admin use only.

    Access:   Admin ONLY  (HR, Manager, Employee are all blocked)
    Throttle: ReportRateThrottle (20 requests/minute — stricter)

    Report Includes:
      - Full payroll summary by department
      - Employee turnover (inactive count by department)
      - Top 10 highest-paid employees
      - Salary band distribution
    """
    permission_classes = [IsAdmin]
    throttle_classes = [ReportRateThrottle]

    def get(self, request):

        # ── Payroll by Department ────────────────────────────────────────────
        payroll_by_dept = list(
            Department.objects.annotate(
                headcount=Count(
                    "employee_set",
                    filter=Q(employee_set__status=True),
                ),
                total_salary=Sum(
                    "employee_set__salary",
                    filter=Q(employee_set__status=True),
                ),
                avg_salary=Avg(
                    "employee_set__salary",
                    filter=Q(employee_set__status=True),
                ),
            )
            .values("id", "name", "headcount", "total_salary", "avg_salary")
            .order_by("-total_salary")
        )
        for dept in payroll_by_dept:
            for key in ("total_salary", "avg_salary"):
                if dept[key] is not None:
                    dept[key] = round(float(dept[key]), 2)

        # ── Top 10 Highest Paid ──────────────────────────────────────────────
        top_paid = list(
            Employee.objects.filter(status=True)
            .select_related("department")
            .order_by("-salary")[:10]
            .values(
                "employee_id", "first_name", "last_name",
                "salary", "designation", "department__name",
            )
        )
        for emp in top_paid:
            if emp["salary"] is not None:
                emp["salary"] = float(emp["salary"])

        # ── Inactive / Turnover Report ───────────────────────────────────────
        inactive_by_dept = list(
            Department.objects.annotate(
                inactive_count=Count(
                    "employee_set",
                    filter=Q(employee_set__status=False),
                ),
            )
            .values("name", "inactive_count")
            .order_by("-inactive_count")
        )

        # ── Salary Band Distribution ─────────────────────────────────────────
        active_employees = Employee.objects.filter(status=True)
        salary_bands = {
            "0_to_30k":    active_employees.filter(salary__lte=30000).count(),
            "30k_to_60k":  active_employees.filter(salary__gt=30000, salary__lte=60000).count(),
            "60k_to_100k": active_employees.filter(salary__gt=60000, salary__lte=100000).count(),
            "above_100k":  active_employees.filter(salary__gt=100000).count(),
        }

        # Audit report access
        create_audit_log(
            user=request.user,
            action="CREATE",
            module="AUTH",
            object_id=request.user.pk,
            details={"action": "report_accessed", "username": request.user.username},
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            data={
                "payroll_by_department": payroll_by_dept,
                "top_10_highest_paid": top_paid,
                "turnover_by_department": inactive_by_dept,
                "salary_band_distribution": salary_bands,
                "report_generated_at": timezone.now().isoformat(),
                "generated_by": request.user.username,
            },
            message="Report generated successfully",
            status_code=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module 11: Report Download API
# GET /api/v1/reports/{id}/download/?format=excel|pdf|csv
# ─────────────────────────────────────────────────────────────────────────────

class ReportDownloadView(APIView):
    """
    Download a generated report by type name.

    Supports:
      - report_id: employee | department | salary | attendance | dashboard
      - format: excel | pdf | csv

    Also stores each generated file as a GeneratedReport model instance.
    """
    permission_classes = [IsManagerOrAbove]

    def get(self, request, pk):
        export_format = request.GET.get('format', 'excel').lower()
        report_id = str(pk).lower()
        valid_reports = ['employee', 'department', 'salary', 'attendance', 'dashboard']

        if report_id not in valid_reports:
            return ErrorResponse(
                message="Invalid report ID. Valid options: employee, department, salary, attendance, dashboard",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if export_format not in ('excel', 'pdf', 'csv'):
            return ErrorResponse(
                message="Invalid format. Valid options: excel, pdf, csv",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            filepath = None
            content_type = None

            if export_format == 'excel':
                from reports.excel_export import generate_employees_excel
                filepath = generate_employees_excel(report_id)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

            elif export_format == 'csv':
                from reports.csv_handler import export_csv
                filepath = export_csv(report_id)
                content_type = 'text/csv; charset=utf-8'

            elif export_format == 'pdf':
                from reports.pdf_generator import (
                    generate_employee_report_pdf,
                    generate_department_report_pdf,
                    generate_salary_report_pdf,
                    generate_attendance_report_pdf,
                    generate_dashboard_report_pdf,
                )
                pdf_dispatch = {
                    'employee': generate_employee_report_pdf,
                    'department': generate_department_report_pdf,
                    'salary': generate_salary_report_pdf,
                    'attendance': generate_attendance_report_pdf,
                    'dashboard': generate_dashboard_report_pdf,
                }
                filepath = pdf_dispatch[report_id]()
                content_type = 'application/pdf'

            # Store the generated report
            from reports.models import GeneratedReport
            from django.core.files import File as DjangoFile

            report_record = GeneratedReport(
                report_type=report_id,
                format=export_format,
                generated_by=request.user,
            )
            with open(filepath, 'rb') as f:
                report_record.file.save(os.path.basename(filepath), DjangoFile(f), save=True)

            # Audit log
            create_audit_log(
                user=request.user,
                action="CREATE",
                module="EMPLOYEE",
                object_id=report_record.pk,
                details={
                    "action": "report_downloaded",
                    "report_type": report_id,
                    "format": export_format,
                },
                ip_address=get_client_ip(request),
            )

            response = FileResponse(
                open(filepath, 'rb'),
                as_attachment=True,
                filename=os.path.basename(filepath),
            )
            response['Content-Type'] = content_type
            return response

        except Exception as e:
            return ErrorResponse(
                message="Report generation failed",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Module 11: Stored Report Download by ID
# GET /api/v1/reports/stored/{id}/download/
# ─────────────────────────────────────────────────────────────────────────────

class StoredReportDownloadView(APIView):
    """
    Download a previously generated and stored report by its database primary key.
    """
    permission_classes = [IsManagerOrAbove]

    def get(self, request, pk):
        from reports.models import GeneratedReport

        try:
            report = GeneratedReport.objects.get(pk=pk)
        except GeneratedReport.DoesNotExist:
            return ErrorResponse(
                message="Report not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if not report.file:
            return ErrorResponse(
                message="Report file not found on disk",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        content_type_map = {
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'csv': 'text/csv; charset=utf-8',
        }

        response = FileResponse(
            report.file.open('rb'),
            as_attachment=True,
            filename=os.path.basename(report.file.name),
        )
        response['Content-Type'] = content_type_map.get(report.format, 'application/octet-stream')
        return response


# ─────────────────────────────────────────────────────────────────────────────
# Module 12: Dashboard Export
# GET /api/v1/dashboard/export/?format=excel|pdf
# ─────────────────────────────────────────────────────────────────────────────

class DashboardExportView(APIView):
    """
    Export dashboard data as Excel or PDF.
    """
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        export_format = request.GET.get('format', 'excel').lower()

        try:
            if export_format == 'excel':
                from reports.excel_export import generate_employees_excel
                filepath = generate_employees_excel('dashboard')
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                filename = 'dashboard_export.xlsx'

            elif export_format == 'pdf':
                from reports.pdf_generator import generate_dashboard_report_pdf
                filepath = generate_dashboard_report_pdf()
                content_type = 'application/pdf'
                filename = 'dashboard_export.pdf'

            elif export_format == 'csv':
                from reports.csv_handler import export_csv
                filepath = export_csv('employee')
                content_type = 'text/csv; charset=utf-8'
                filename = 'dashboard_export.csv'

            else:
                return ErrorResponse(
                    message="Invalid format. Valid options: excel, pdf, csv",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            response = FileResponse(
                open(filepath, 'rb'),
                as_attachment=True,
                filename=filename,
            )
            response['Content-Type'] = content_type
            return response

        except Exception as e:
            return ErrorResponse(
                message="Dashboard export failed",
                errors=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Module 8: Employee QR Code API
# GET /api/v1/employees/{id}/qr-code/
# ─────────────────────────────────────────────────────────────────────────────

class EmployeeQRCodeView(APIView):
    """
    Generate and return an employee's QR code as a PNG image.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            employee = Employee.objects.select_related('department').get(pk=pk)
        except Employee.DoesNotExist:
            return ErrorResponse(
                message="Employee not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        from reports.qr_generator import generate_employee_qr
        qr_path = generate_employee_qr(employee)

        if not os.path.exists(qr_path):
            return ErrorResponse(
                message="QR code generation failed",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = FileResponse(
            open(qr_path, 'rb'),
            content_type='image/png',
        )
        response['Content-Disposition'] = f'inline; filename="QR_{employee.employee_id}.png"'
        return response
