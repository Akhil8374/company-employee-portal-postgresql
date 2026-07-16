import os
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from .qr_generator import generate_employee_qr

def get_pdf_dir(sub_dir):
    pdf_dir = os.path.join(settings.MEDIA_ROOT, sub_dir)
    os.makedirs(pdf_dir, exist_ok=True)
    return pdf_dir

def generate_employee_profile_pdf(employee):
    filepath = os.path.join(get_pdf_dir('profiles'), f"{employee.employee_id}_Profile.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"Employee Profile: {employee.first_name} {employee.last_name}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))

    data = [
        ['Employee ID', employee.employee_id],
        ['Name', f"{employee.first_name} {employee.last_name}"],
        ['Email', employee.email],
        ['Phone', employee.phone],
        ['Department', employee.department.name if employee.department else 'N/A'],
        ['Designation', employee.designation],
        ['Salary', f"${employee.salary:,.2f}"],
        ['Joining Date', employee.joining_date.strftime('%Y-%m-%d') if employee.joining_date else 'N/A'],
        ['Status', 'Active' if employee.status else 'Inactive']
    ]

    t = Table(data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t)
    
    doc.build(elements)
    return filepath

def generate_salary_slip_pdf(employee, month, year):
    filename = f"SalarySlip_{month}_{year}_{employee.employee_id}.pdf"
    filepath = os.path.join(get_pdf_dir('salary_slips'), filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Company Name", styles['Title']))
    elements.append(Paragraph(f"Salary Slip for {month} {year}", styles['Heading2']))
    elements.append(Spacer(1, 0.25*inch))

    # Basic Salary Calculations (Mock)
    basic_salary = float(employee.salary)
    allowances = basic_salary * 0.20
    deductions = basic_salary * 0.10
    net_salary = basic_salary + allowances - deductions

    data = [
        ['Employee ID', employee.employee_id, 'Name', f"{employee.first_name} {employee.last_name}"],
        ['Department', employee.department.name if employee.department else '', 'Designation', employee.designation],
        ['', '', '', ''],
        ['Earnings', 'Amount', 'Deductions', 'Amount'],
        ['Basic Salary', f"${basic_salary:,.2f}", 'Tax/PF', f"${deductions:,.2f}"],
        ['Allowances', f"${allowances:,.2f}", '', ''],
        ['', '', '', ''],
        ['Net Salary', '', '', f"${net_salary:,.2f}"]
    ]

    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 3), (-1, 3), colors.grey),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (1, 7), (2, 7))
    ]))
    elements.append(t)
    
    doc.build(elements)
    return filepath

def generate_id_card_pdf(employee):
    filename = f"ID_{employee.employee_id}.pdf"
    filepath = os.path.join(get_pdf_dir('id_cards'), filename)
    
    # Standard ID card size: 3.375 x 2.125 inches
    c = canvas.Canvas(filepath, pagesize=(3.375*inch, 2.125*inch))
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.2*inch, 1.8*inch, "Company Logo")
    
    c.setFont("Helvetica", 10)
    c.drawString(0.2*inch, 1.5*inch, f"Name: {employee.first_name} {employee.last_name}")
    c.drawString(0.2*inch, 1.3*inch, f"ID: {employee.employee_id}")
    c.drawString(0.2*inch, 1.1*inch, f"Dept: {employee.department.name if employee.department else ''}")
    
    # Calculate validity (1 year from now)
    validity = datetime.now().replace(year=datetime.now().year + 1).strftime('%Y-%m-%d')
    c.drawString(0.2*inch, 0.9*inch, f"Valid Till: {validity}")
    
    qr_path = generate_employee_qr(employee)
    c.drawImage(qr_path, 2.2*inch, 0.9*inch, width=1*inch, height=1*inch)
    
    # If employee has profile_photo, draw it (omitted for simplicity, but easily addable)
    if employee.profile_photo:
        photo_path = employee.profile_photo.path
        if os.path.exists(photo_path):
            c.drawImage(photo_path, 2.2*inch, 1.2*inch, width=0.8*inch, height=0.8*inch, preserveAspectRatio=True)

    c.save()
    return filepath


# ──────────────────────────────────────────────────────────────────────────────
# Report PDF Generators (Module 10)
# ──────────────────────────────────────────────────────────────────────────────

def generate_employee_report_pdf():
    """Generate an Employee Report PDF with active/inactive summary."""
    from employees.models import Employee

    filepath = os.path.join(get_pdf_dir('reports'), f"employee_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Employee Report", styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    # Summary
    total = Employee.objects.count()
    active = Employee.objects.filter(status=True).count()
    inactive = Employee.objects.filter(status=False).count()

    summary_data = [
        ['Metric', 'Count'],
        ['Total Employees', str(total)],
        ['Active Employees', str(active)],
        ['Inactive Employees', str(inactive)],
    ]
    t = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.25 * inch))

    # Employee listing
    elements.append(Paragraph("Employee List", styles['Heading2']))
    emp_data = [['ID', 'Name', 'Department', 'Designation', 'Status']]
    for emp in Employee.objects.select_related('department').all()[:100]:
        emp_data.append([
            emp.employee_id,
            f"{emp.first_name} {emp.last_name}",
            emp.department.name if emp.department else 'N/A',
            emp.designation,
            'Active' if emp.status else 'Inactive',
        ])
    t2 = Table(emp_data, colWidths=[1 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t2)

    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

    doc.build(elements)
    return filepath


def generate_department_report_pdf():
    """Generate a Department Report PDF with employee count and avg salary."""
    from employees.models import Department
    from django.db.models import Count, Avg, Q

    filepath = os.path.join(get_pdf_dir('reports'), f"department_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Department Report", styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    dept_stats = Department.objects.annotate(
        employee_count=Count("employee_set"),
        active_count=Count("employee_set", filter=Q(employee_set__status=True)),
        inactive_count=Count("employee_set", filter=Q(employee_set__status=False)),
        avg_salary=Avg("employee_set__salary", filter=Q(employee_set__status=True)),
    )

    data = [['Department', 'Total', 'Active', 'Inactive', 'Avg Salary']]
    for dept in dept_stats:
        data.append([
            dept.name,
            str(dept.employee_count),
            str(dept.active_count),
            str(dept.inactive_count),
            f"${float(dept.avg_salary or 0):,.2f}",
        ])

    t = Table(data, colWidths=[2 * inch, 1 * inch, 1 * inch, 1 * inch, 1.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)

    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

    doc.build(elements)
    return filepath


def generate_salary_report_pdf():
    """Generate a Salary Report PDF with monthly payroll and department salary summary."""
    from employees.models import Employee, Department
    from django.db.models import Sum, Avg, Q

    filepath = os.path.join(get_pdf_dir('reports'), f"salary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Salary Report", styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    # Overall payroll summary
    active = Employee.objects.filter(status=True)
    total_payroll = float(active.aggregate(total=Sum('salary'))['total'] or 0)

    elements.append(Paragraph(f"Monthly Payroll Total: ${total_payroll:,.2f}", styles['Heading2']))
    elements.append(Spacer(1, 0.15 * inch))

    # Department salary summary
    elements.append(Paragraph("Department Salary Summary", styles['Heading3']))
    dept_stats = Department.objects.annotate(
        headcount=Sum("employee_set__pk", filter=Q(employee_set__status=True), default=0),
        total_salary=Sum("employee_set__salary", filter=Q(employee_set__status=True)),
        avg_salary=Avg("employee_set__salary", filter=Q(employee_set__status=True)),
    )

    data = [['Department', 'Headcount', 'Total Salary', 'Avg Salary']]
    for dept in dept_stats:
        from django.db.models import Count as Cnt
        hc = Employee.objects.filter(department=dept, status=True).count()
        data.append([
            dept.name,
            str(hc),
            f"${float(dept.total_salary or 0):,.2f}",
            f"${float(dept.avg_salary or 0):,.2f}",
        ])

    t = Table(data, colWidths=[2 * inch, 1.2 * inch, 1.8 * inch, 1.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.15 * inch))

    # Top earners
    elements.append(Paragraph("Top 10 Highest-Paid Employees", styles['Heading3']))
    top_data = [['ID', 'Name', 'Department', 'Salary']]
    for emp in active.select_related('department').order_by('-salary')[:10]:
        top_data.append([
            emp.employee_id,
            f"{emp.first_name} {emp.last_name}",
            emp.department.name if emp.department else 'N/A',
            f"${float(emp.salary):,.2f}",
        ])

    t2 = Table(top_data, colWidths=[1.2 * inch, 2 * inch, 2 * inch, 1.3 * inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t2)

    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

    doc.build(elements)
    return filepath


def generate_attendance_report_pdf():
    """Generate an Attendance Report PDF with present/absent/leave counts."""
    from employees.models import Attendance
    from django.db.models import Count, Q

    filepath = os.path.join(get_pdf_dir('reports'), f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Attendance Report", styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    # Overall summary
    total = Attendance.objects.count()
    present = Attendance.objects.filter(status='PRESENT').count()
    absent = Attendance.objects.filter(status='ABSENT').count()
    leave = Attendance.objects.filter(status='LEAVE').count()
    half_day = Attendance.objects.filter(status='HALF_DAY').count()

    summary_data = [
        ['Status', 'Count'],
        ['Total Records', str(total)],
        ['Present', str(present)],
        ['Absent', str(absent)],
        ['Leave', str(leave)],
        ['Half Day', str(half_day)],
    ]
    t = Table(summary_data, colWidths=[3 * inch, 2 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.25 * inch))

    # Recent attendance records
    elements.append(Paragraph("Recent Attendance Records", styles['Heading2']))
    att_data = [['Date', 'Employee ID', 'Name', 'Status']]
    for att in Attendance.objects.select_related('employee').order_by('-date')[:50]:
        att_data.append([
            att.date.strftime('%Y-%m-%d') if att.date else '',
            att.employee.employee_id,
            f"{att.employee.first_name} {att.employee.last_name}",
            att.status,
        ])

    t2 = Table(att_data, colWidths=[1.5 * inch, 1.5 * inch, 2 * inch, 1.5 * inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C0392B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t2)

    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

    doc.build(elements)
    return filepath


def generate_dashboard_report_pdf():
    """Generate a combined Dashboard Report PDF."""
    from employees.models import Employee, Department, Attendance
    from django.db.models import Count, Avg, Sum, Max, Min, Q
    from django.utils import timezone

    filepath = os.path.join(get_pdf_dir('reports'), f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("HRMS Dashboard Report", styles['Title']))
    elements.append(Spacer(1, 0.25 * inch))

    today = timezone.now().date()

    # Employee Summary
    elements.append(Paragraph("Employee Summary", styles['Heading2']))
    total = Employee.objects.count()
    active = Employee.objects.filter(status=True).count()
    inactive = Employee.objects.filter(status=False).count()
    dept_count = Department.objects.count()

    summary_data = [
        ['Metric', 'Value'],
        ['Total Employees', str(total)],
        ['Active Employees', str(active)],
        ['Inactive Employees', str(inactive)],
        ['Total Departments', str(dept_count)],
    ]
    t = Table(summary_data, colWidths=[3 * inch, 2.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.2 * inch))

    # Salary Statistics
    elements.append(Paragraph("Salary Statistics", styles['Heading2']))
    stats = Employee.objects.filter(status=True).aggregate(
        total_payroll=Sum('salary'),
        avg_salary=Avg('salary'),
        max_salary=Max('salary'),
        min_salary=Min('salary'),
    )
    sal_data = [
        ['Metric', 'Value'],
        ['Total Monthly Payroll', f"${float(stats['total_payroll'] or 0):,.2f}"],
        ['Average Salary', f"${float(stats['avg_salary'] or 0):,.2f}"],
        ['Highest Salary', f"${float(stats['max_salary'] or 0):,.2f}"],
        ['Lowest Salary', f"${float(stats['min_salary'] or 0):,.2f}"],
    ]
    t2 = Table(sal_data, colWidths=[3 * inch, 2.5 * inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 0.2 * inch))

    # Today's Attendance
    elements.append(Paragraph(f"Attendance Summary ({today})", styles['Heading2']))
    att_today = Attendance.objects.filter(date=today)
    att_data = [
        ['Status', 'Count'],
        ['Present', str(att_today.filter(status='PRESENT').count())],
        ['Absent', str(att_today.filter(status='ABSENT').count())],
        ['Leave', str(att_today.filter(status='LEAVE').count())],
        ['Half Day', str(att_today.filter(status='HALF_DAY').count())],
    ]
    t3 = Table(att_data, colWidths=[3 * inch, 2.5 * inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(t3)

    elements.append(Spacer(1, 0.25 * inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

    doc.build(elements)
    return filepath

