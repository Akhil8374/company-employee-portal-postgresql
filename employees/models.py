from django.db import models
from .managers import EmployeeManager


class Department(models.Model):
    name = models.CharField(max_length=100)
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

    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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