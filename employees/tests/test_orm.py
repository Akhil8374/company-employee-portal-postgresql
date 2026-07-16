from datetime import date

from django.test import TestCase

from employees.models import Department, Employee


class EmployeeORMTest(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name="Development",
            description="Software Development Department"
        )

        self.employee = Employee.objects.create(
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

    # Create
    def test_create_employee(self):

        employee = Employee.objects.create(
            employee_id="EMP002",
            first_name="Rahul",
            last_name="Sharma",
            email="rahul@test.com",
            phone="9999999999",
            salary=45000,
            joining_date=date.today(),
            designation="Backend Developer",
            department=self.department,
        )

        self.assertEqual(Employee.objects.count(), 2)
        self.assertEqual(employee.first_name, "Rahul")

    # Update
    def test_update_employee(self):

        self.employee.first_name = "Updated"
        self.employee.salary = 70000
        self.employee.save()

        updated = Employee.objects.get(pk=self.employee.pk)

        self.assertEqual(updated.first_name, "Updated")
        self.assertEqual(updated.salary, 70000)

    # Delete
    def test_delete_employee(self):

        self.employee.delete()

        self.assertEqual(Employee.objects.count(), 0)

    # Search
    def test_search_employee(self):

        employee = Employee.objects.get(
            employee_id="EMP001"
        )

        self.assertEqual(employee.email, "akhil@test.com")

    # Filter
    def test_filter_employee(self):

        Employee.objects.create(
            employee_id="EMP002",
            first_name="Ravi",
            last_name="Kumar",
            email="ravi@test.com",
            phone="8888888888",
            salary=35000,
            joining_date=date.today(),
            designation="Tester",
            department=self.department,
        )

        developers = Employee.objects.filter(
            designation="Python Developer"
        )

        self.assertEqual(developers.count(), 1)

    # Department Relationship
    def test_department_relationship(self):

        self.assertEqual(
            self.employee.department.name,
            "Development"
        )

        self.assertEqual(
            self.department.employee_set.count(),
            1
        )

    # Manager Relationship
    def test_manager_relationship(self):

        manager = Employee.objects.create(
            employee_id="EMP100",
            first_name="Manager",
            last_name="One",
            email="manager@test.com",
            phone="7777777777",
            salary=90000,
            joining_date=date.today(),
            designation="Manager",
            department=self.department,
        )

        employee = Employee.objects.create(
            employee_id="EMP101",
            first_name="Employee",
            last_name="One",
            email="employee@test.com",
            phone="6666666666",
            salary=40000,
            joining_date=date.today(),
            designation="Developer",
            department=self.department,
            manager=manager,
        )

        self.assertEqual(employee.manager.first_name, "Manager")
        self.assertEqual(manager.subordinates.count(), 1)