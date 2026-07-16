import csv
import os
from datetime import datetime
from django.conf import settings
from employees.models import Employee, Department
from django.db import transaction

def get_reports_dir():
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir

def export_employees_csv():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"employees_{timestamp}.csv"
    filepath = os.path.join(get_reports_dir(), filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Employee ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Department', 'Designation', 'Salary', 'Joining Date'])

        employees = Employee.objects.select_related('department').all()
        for emp in employees:
            writer.writerow([
                emp.employee_id,
                emp.first_name,
                emp.last_name,
                emp.email,
                emp.phone,
                emp.department.name if emp.department else '',
                emp.designation,
                emp.salary,
                emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else ''
            ])
    return filepath

def import_employees_csv(file_obj):
    # file_obj is an InMemoryUploadedFile
    decoded_file = file_obj.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    
    # Header Validation
    required_headers = {'Employee ID', 'First Name', 'Email', 'Department'}
    if not required_headers.issubset(set(reader.fieldnames or [])):
        raise ValueError(f"Missing required headers. Expected at least: {required_headers}")

    total_rows = 0
    created = 0
    failed = 0
    errors = []
    
    # Duplicate Detection
    existing_emails = set(Employee.objects.values_list('email', flat=True))
    existing_ids = set(Employee.objects.values_list('employee_id', flat=True))

    for idx, row in enumerate(reader, start=2):
        total_rows += 1
        emp_id = row.get('Employee ID')
        first_name = row.get('First Name')
        last_name = row.get('Last Name', '')
        email = row.get('Email')
        phone = row.get('Phone', '')
        dept_name = row.get('Department')
        designation = row.get('Designation', '')
        salary = row.get('Salary', 0)
        joining_date = row.get('Joining Date')

        if not all([emp_id, first_name, email, dept_name]):
            failed += 1
            errors.append({"row": idx, "error": "Missing required fields"})
            continue

        if email in existing_emails or emp_id in existing_ids:
            failed += 1
            errors.append({"row": idx, "error": "Duplicate entry detected (Email or Employee ID already exists)"})
            continue

        try:
            department, _ = Department.objects.get_or_create(name=dept_name)
            
            with transaction.atomic():
                Employee.objects.create(
                    employee_id=emp_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    department=department,
                    designation=designation,
                    salary=float(salary) if salary else 0.0,
                    joining_date=joining_date or None
                )
            
            existing_emails.add(email)
            existing_ids.add(emp_id)
            created += 1

        except Exception as e:
            failed += 1
            errors.append({"row": idx, "error": str(e)})

    return {
        "total_rows": total_rows,
        "created": created,
        "failed": failed,
        "errors": errors
    }


def export_department_csv():
    """Export department summary to CSV."""
    from django.db.models import Count, Avg, Q

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"departments_{timestamp}.csv"
    filepath = os.path.join(get_reports_dir(), filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Department', 'Employee Count', 'Active', 'Inactive', 'Average Salary'])

        dept_stats = Department.objects.annotate(
            employee_count=Count("employee_set"),
            active_count=Count("employee_set", filter=Q(employee_set__status=True)),
            inactive_count=Count("employee_set", filter=Q(employee_set__status=False)),
            avg_salary=Avg("employee_set__salary", filter=Q(employee_set__status=True)),
        )
        for dept in dept_stats:
            writer.writerow([
                dept.name,
                dept.employee_count,
                dept.active_count,
                dept.inactive_count,
                round(float(dept.avg_salary or 0), 2),
            ])
    return filepath


def export_salary_csv():
    """Export salary report to CSV."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"salary_report_{timestamp}.csv"
    filepath = os.path.join(get_reports_dir(), filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Employee ID', 'Name', 'Department', 'Designation', 'Salary'])

        employees = Employee.objects.select_related('department').filter(status=True).order_by('-salary')
        for emp in employees:
            writer.writerow([
                emp.employee_id,
                f"{emp.first_name} {emp.last_name}",
                emp.department.name if emp.department else '',
                emp.designation,
                float(emp.salary),
            ])
    return filepath


def export_attendance_csv():
    """Export attendance records to CSV."""
    from employees.models import Attendance

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"attendance_{timestamp}.csv"
    filepath = os.path.join(get_reports_dir(), filename)

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Employee ID', 'Name', 'Status'])

        attendances = Attendance.objects.select_related('employee').all().order_by('-date')
        for att in attendances:
            writer.writerow([
                att.date.strftime('%Y-%m-%d') if att.date else '',
                att.employee.employee_id,
                f"{att.employee.first_name} {att.employee.last_name}",
                att.status,
            ])
    return filepath


def export_csv(export_type='employee'):
    """
    Dispatcher function: export any report type to CSV.
    Matches the interface of `generate_employees_excel(export_type)`.
    """
    dispatch = {
        'employee': export_employees_csv,
        'department': export_department_csv,
        'salary': export_salary_csv,
        'attendance': export_attendance_csv,
    }
    handler = dispatch.get(export_type, export_employees_csv)
    return handler()
