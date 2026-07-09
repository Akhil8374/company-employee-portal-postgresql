from django.db import models
from employees.models import Employee
from .validators import validate_pdf, validate_file_size

class EmployeeDocument(models.Model):
    DOCUMENT_TYPES = [
        ('RESUME', 'Resume'),
        ('AADHAAR', 'Aadhaar'),
        ('PAN', 'PAN'),
        ('DEGREE_CERTIFICATE', 'Degree Certificate'),
        ('EXPERIENCE_CERTIFICATE', 'Experience Certificate'),
        ('OFFER_LETTER', 'Offer Letter'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/', validators=[validate_pdf, validate_file_size])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} ({self.employee.employee_id})"
