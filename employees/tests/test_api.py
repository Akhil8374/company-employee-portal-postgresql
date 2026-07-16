from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from employees.models import Department, Employee


# ==========================================================
# Authentication API Tests
# ==========================================================

class AuthenticationAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="Admin@123",
            email="admin@test.com",
            role="ADMIN",
        )

    def test_login_success(self):

        response = self.client.post(
            reverse("v1:login"),
            {
                "username": "admin",
                "password": "Admin@123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data["data"],
        )

        self.assertIn(
            "refresh",
            response.data["data"],
        )

    def test_login_invalid_password(self):

        response = self.client.post(
            reverse("v1:login"),
            {
                "username": "admin",
                "password": "wrongpassword",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_login_without_credentials(self):

        response = self.client.post(
            reverse("v1:login"),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


# ==========================================================
# Employee API Tests
# ==========================================================

class EmployeeAPITest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="admin",
            password="Admin@123",
            email="admin2@test.com",
            role="ADMIN",
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        self.department = Department.objects.create(
            name="Development",
            description="Software Development",
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
            status=True,
        )

    def test_get_employee_list(self):

        response = self.client.get(
            reverse("v1:employee-list-create")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_get_employee_detail(self):

        response = self.client.get(
            reverse(
                "v1:employee-detail",
                args=[self.employee.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_create_employee(self):

        payload = {
            "employee_id": "EMP002",
            "first_name": "Rahul",
            "last_name": "Sharma",
            "email": "rahul@test.com",
            "phone": "9999999999",
            "salary": "60000.00",
            "joining_date": str(date.today()),
            "designation": "Backend Developer",
            "department": self.department.id,
            "status": True,
        }

        response = self.client.post(
            reverse("v1:employee-list-create"),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_update_employee(self):

        payload = {
            "first_name": "Updated"
        }

        response = self.client.put(
            reverse(
                "v1:employee-detail",
                args=[self.employee.id],
            ),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_delete_employee(self):

        response = self.client.delete(
            reverse(
                "v1:employee-detail",
                args=[self.employee.id],
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_employee_api_without_token(self):

        self.client.credentials()

        response = self.client.get(
            reverse("v1:employee-list-create")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_employee_invalid_data(self):

        response = self.client.post(
            reverse("v1:employee-list-create"),
            {
                "first_name": "OnlyName",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )