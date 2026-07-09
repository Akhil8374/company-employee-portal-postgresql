from django.db import models
from documents.validators import (
    validate_pdf,
    validate_file_size,
    validate_image,
)

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField()
    designation = models.CharField(max_length=100)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="employee_set",
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )

    profile_photo = models.ImageField(
        upload_to="employees/photos/",
        blank=True,
        null=True,
        validators=[validate_image, validate_file_size],

    )

    resume = models.FileField(upload_to='employees/resumes/', null=True, blank=True, validators=[validate_pdf, validate_file_size])
    aadhaar_document = models.FileField(upload_to='employees/aadhaar/', null=True, blank=True, validators=[validate_pdf, validate_file_size])
    pan_document = models.FileField(upload_to='employees/pan/', null=True, blank=True, validators=[validate_pdf, validate_file_size])

    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LEAVE', 'Leave'),
        ('HALF_DAY', 'Half Day'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.status}"