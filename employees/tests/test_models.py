from datetime import date
from django.db import IntegrityError
from django.test import TestCase

from employees.models import Department, Employee


class DepartmentModelTest(TestCase):

    def test_department_creation(self):
        department = Department.objects.create(
            name="HR",
            description="Human Resource Department"
        )

        self.assertEqual(department.name, "HR")
        self.assertEqual(
            Department.objects.count(),
            1
        )


class EmployeeModelTest(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name="Development",
            description="Software Development"
        )

    def test_employee_creation(self):

        employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="Akhil",
            last_name="Rao",
            email="akhil@test.com",
            phone="9876543210",
            salary=50000,
            joining_date=date.today(),
            designation="Python Developer",
            department=self.department,
        )

        self.assertEqual(employee.first_name, "Akhil")
        self.assertEqual(employee.department.name, "Development")
        self.assertEqual(Employee.objects.count(), 1)

    def test_unique_employee_id(self):

        Employee.objects.create(
            employee_id="EMP001",
            first_name="A",
            last_name="B",
            email="a@test.com",
            phone="9999999999",
            salary=40000,
            joining_date=date.today(),
            designation="Developer",
            department=self.department,
        )

        with self.assertRaises(IntegrityError):

            Employee.objects.create(
                employee_id="EMP001",
                first_name="C",
                last_name="D",
                email="c@test.com",
                phone="8888888888",
                salary=45000,
                joining_date=date.today(),
                designation="Developer",
                department=self.department,
            )

    def test_unique_email(self):

        Employee.objects.create(
            employee_id="EMP001",
            first_name="A",
            last_name="B",
            email="same@test.com",
            phone="9999999999",
            salary=40000,
            joining_date=date.today(),
            designation="Developer",
            department=self.department,
        )

        with self.assertRaises(IntegrityError):

            Employee.objects.create(
                employee_id="EMP002",
                first_name="C",
                last_name="D",
                email="same@test.com",
                phone="8888888888",
                salary=45000,
                joining_date=date.today(),
                designation="Developer",
                department=self.department,
            )

    def test_employee_string_representation(self):

        employee = Employee.objects.create(
            employee_id="EMP100",
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            phone="9876543211",
            salary=60000,
            joining_date=date.today(),
            designation="Manager",
            department=self.department,
        )

        self.assertEqual(str(employee), "John Doe")

    def test_department_string_representation(self):

        self.assertEqual(
            str(self.department),
            "Development"
        )