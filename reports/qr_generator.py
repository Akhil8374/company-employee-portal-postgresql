import qrcode
import os
from django.conf import settings

def get_qr_dir():
    qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)
    return qr_dir

def generate_employee_qr(employee):
    """
    Generates a QR code for an employee and returns the file path.
    """
    verification_url = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'http://localhost:8000'}/api/v1/employees/{employee.id}/"
    qr_data = (
        f"Employee ID: {employee.employee_id}\n"
        f"Name: {employee.first_name} {employee.last_name}\n"
        f"Department: {employee.department.name if employee.department else 'N/A'}\n"
        f"Verification URL: {verification_url}"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    filename = f"QR_{employee.employee_id}.png"
    filepath = os.path.join(get_qr_dir(), filename)
    img.save(filepath)
    
    return filepath
