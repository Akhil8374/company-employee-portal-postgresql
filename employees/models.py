from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from .managers import EmployeeManager


class Department(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    employee_id = models.CharField(
    max_length=20,
    unique=True,
    db_index=True,
)
    
    first_name = models.CharField(max_length=100, db_index=True)
    last_name = models.CharField(max_length=100, db_index=True)
    email = models.EmailField(
    unique=True,
    db_index=True,
)
    phone = models.CharField(max_length=15)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    joining_date = models.DateField(
    db_index=True,
)
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

    profile_image = models.ImageField(
        upload_to="employees/",
        blank=True,
        null=True,
    )

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="employees",
    )

    objects = EmployeeManager()

    status = models.BooleanField(
    default=True,
    db_index=True,
)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        """
        Model-level validation.
        - Salary cannot be negative.
        - Joining date cannot be in the future.
        - Employee ID cannot be changed after creation.
        """
        super().clean()

        # Salary cannot be negative
        if self.salary is not None and self.salary < 0:
            raise ValidationError(
                {"salary": "Salary cannot be negative."}
            )

        # Joining date cannot be in the future
        if self.joining_date and self.joining_date > timezone.now().date():
            raise ValidationError(
                {"joining_date": "Joining date cannot be in the future."}
            )

        # Employee ID cannot be changed after creation
        if self.pk:
            try:
                original = Employee.objects.get(pk=self.pk)
                if original.employee_id != self.employee_id:
                    raise ValidationError(
                        {"employee_id": "Employee ID cannot be changed after creation."}
                    )
            except Employee.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        """Override save to run full_clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class EmployeeProfile(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Short biography of the employee.")
    photo = models.ImageField(
        upload_to="employee_profiles/",
        blank=True,
        null=True,
        help_text="Profile photo.",
    )

    def __str__(self):
        return self.employee.first_name


class Payroll(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    processed_on = models.DateTimeField(
        auto_now_add=True,
    )

    status = models.CharField(
        max_length=30,
        default="SUCCESS",
    )

    def __str__(self):
        return f"{self.employee} - {self.amount}"


class Attendance(models.Model):
    """
    Model representing employee daily attendance.
    """
    STATUS_CHOICES = [
        ("PRESENT", "Present"),
        ("ABSENT", "Absent"),
        ("LEAVE", "Leave"),
        ("HALF_DAY", "Half Day"),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )
    date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PRESENT",
        db_index=True,
    )
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"