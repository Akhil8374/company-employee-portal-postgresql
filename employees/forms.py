from django import forms
from django.utils import timezone
import re

from .models import Employee


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = "__all__"

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"]

        if not re.match(r"^EMP\d+$", employee_id):
            raise forms.ValidationError(
                "Employee ID must be like EMP001"
            )

        employee = Employee.objects.filter(employee_id=employee_id)

        if self.instance.pk:
            employee = employee.exclude(pk=self.instance.pk)

        if employee.exists():
            raise forms.ValidationError(
                "Employee ID already exists"
            )

        return employee_id

    def clean_email(self):
        email = self.cleaned_data["email"]

        employee = Employee.objects.filter(email=email)

        if self.instance.pk:
            employee = employee.exclude(pk=self.instance.pk)

        if employee.exists():
            raise forms.ValidationError(
                "Email already exists"
            )

        return email

    def clean_salary(self):
        salary = self.cleaned_data["salary"]

        if salary < 10000:
            raise forms.ValidationError(
                "Minimum salary is 10000"
            )

        if salary > 500000:
            raise forms.ValidationError(
                "Maximum salary is 500000"
            )

        return salary

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        if not re.match(r"^\d{10}$", phone):
            raise forms.ValidationError(
                "Phone number must contain exactly 10 digits"
            )

        return phone

    def clean_joining_date(self):
        joining_date = self.cleaned_data["joining_date"]

        if joining_date > timezone.now().date():
            raise forms.ValidationError(
                "Joining date cannot be a future date"
            )

        return joining_date