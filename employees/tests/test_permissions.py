from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory

from accounts.models import User
from api.permissions.role_permissions import (
    IsAdmin,
    IsHROrAdmin,
    IsManagerOrAbove,
)


class PermissionTest(APITestCase):

    def setUp(self):

        self.factory = APIRequestFactory()

        self.admin = User.objects.create_user(
            username="admin",
            password="Admin@123",
            role="ADMIN",
        )

        self.hr = User.objects.create_user(
            username="hr",
            password="Hr@123",
            role="HR",
        )

        self.manager = User.objects.create_user(
            username="manager",
            password="Manager@123",
            role="MANAGER",
        )

        self.employee = User.objects.create_user(
            username="employee",
            password="Employee@123",
            role="EMPLOYEE",
        )

        self.admin_permission = IsAdmin()
        self.hr_permission = IsHROrAdmin()
        self.manager_permission = IsManagerOrAbove()

    # -------------------------
    # Admin Permission
    # -------------------------

    def test_admin_has_access(self):

        request = self.factory.get("/")
        request.user = self.admin

        self.assertTrue(
            self.admin_permission.has_permission(
                request,
                None,
            )
        )

    def test_employee_cannot_access_admin(self):

        request = self.factory.get("/")
        request.user = self.employee

        self.assertFalse(
            self.admin_permission.has_permission(
                request,
                None,
            )
        )

    # -------------------------
    # HR Permission
    # -------------------------

    def test_hr_has_access(self):

        request = self.factory.get("/")
        request.user = self.hr

        self.assertTrue(
            self.hr_permission.has_permission(
                request,
                None,
            )
        )

    def test_admin_has_hr_permission(self):

        request = self.factory.get("/")
        request.user = self.admin

        self.assertTrue(
            self.hr_permission.has_permission(
                request,
                None,
            )
        )

    def test_employee_cannot_access_hr_permission(self):

        request = self.factory.get("/")
        request.user = self.employee

        self.assertFalse(
            self.hr_permission.has_permission(
                request,
                None,
            )
        )

    # -------------------------
    # Manager Permission
    # -------------------------

    def test_manager_has_access(self):

        request = self.factory.get("/")
        request.user = self.manager

        self.assertTrue(
            self.manager_permission.has_permission(
                request,
                None,
            )
        )

    def test_hr_has_manager_permission(self):

        request = self.factory.get("/")
        request.user = self.hr

        self.assertTrue(
            self.manager_permission.has_permission(
                request,
                None,
            )
        )

    def test_admin_has_manager_permission(self):

        request = self.factory.get("/")
        request.user = self.admin

        self.assertTrue(
            self.manager_permission.has_permission(
                request,
                None,
            )
        )

    def test_employee_cannot_access_manager_permission(self):

        request = self.factory.get("/")
        request.user = self.employee

        self.assertFalse(
            self.manager_permission.has_permission(
                request,
                None,
            )
        )
    