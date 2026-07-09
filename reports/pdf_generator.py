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
