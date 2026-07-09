import os
from datetime import datetime
from openpyxl import Workbook
from django.conf import settings
from employees.models import Employee, Department, Attendance
from django.db.models import Count, Avg, Sum, Q

def get_reports_dir():
    # Store temporary reports in media/reports
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir

def generate_employees_excel(export_type='employee'):
    wb = Workbook()
    ws = wb.active
    ws.title = f"{export_type.capitalize()} Report"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{export_type}_report_{timestamp}.xlsx"
    filepath = os.path.join(get_reports_dir(), filename)

    if export_type == 'employee':
        ws.append(['Employee ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Department', 'Designation', 'Status', 'Joining Date'])
        employees = Employee.objects.select_related('department').all()
        for emp in employees:
            ws.append([
                emp.employee_id,
                emp.first_name,
                emp.last_name,
                emp.email,
                emp.phone,
                emp.department.name if emp.department else '',
                emp.designation,
                'Active' if emp.status else 'Inactive',
                emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else ''
            ])

    elif export_type == 'department':
        ws.append(['Department Name', 'Employee Count', 'Active Employees', 'Inactive Employees', 'Average Salary'])
        dept_stats = Department.objects.annotate(
            employee_count=Count("employee_set"),
            active_count=Count("employee_set", filter=Q(employee_set__status=True)),
            inactive_count=Count("employee_set", filter=Q(employee_set__status=False)),
            avg_salary=Avg("employee_set__salary", filter=Q(employee_set__status=True)),
        )
        for dept in dept_stats:
            ws.append([
                dept.name,
                dept.employee_count,
                dept.active_count,
                dept.inactive_count,
                round(float(dept.avg_salary or 0), 2)
            ])

    elif export_type == 'salary':
        ws.append(['Employee ID', 'Name', 'Department', 'Designation', 'Salary'])
        employees = Employee.objects.select_related('department').filter(status=True).order_by('-salary')
        for emp in employees:
            ws.append([
                emp.employee_id,
                f"{emp.first_name} {emp.last_name}",
                emp.department.name if emp.department else '',
                emp.designation,
                float(emp.salary)
            ])

    elif export_type == 'attendance':
        ws.append(['Date', 'Employee ID', 'Name', 'Status'])
        attendances = Attendance.objects.select_related('employee').all().order_by('-date')
        for att in attendances:
            ws.append([
                att.date.strftime('%Y-%m-%d') if att.date else '',
                att.employee.employee_id,
                f"{att.employee.first_name} {att.employee.last_name}",
                att.status
            ])
            
    else:
        ws.append(['Unknown export type'])

    wb.save(filepath)
    return filepath
