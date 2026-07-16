from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User


class AuthenticationFeatureTest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="admin",
            password="Admin@123",
            email="admin@test.com",
            role="ADMIN",
        )

        self.refresh = RefreshToken.for_user(self.user)

        self.access_token = str(self.refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

    # -----------------------------------------------------
    # Login
    # -----------------------------------------------------

    def test_login(self):

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

    # -----------------------------------------------------
    # Refresh Token
    # -----------------------------------------------------

    def test_refresh_token(self):

        response = self.client.post(
            reverse("v1:token-refresh"),
            {
                "refresh": str(self.refresh),
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

    # -----------------------------------------------------
    # Invalid Refresh Token
    # -----------------------------------------------------

    def test_invalid_refresh_token(self):

        response = self.client.post(
            reverse("v1:token-refresh"),
            {
                "refresh": "invalid_token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # -----------------------------------------------------
    # Missing Refresh Token
    # -----------------------------------------------------

    def test_missing_refresh_token(self):

        response = self.client.post(
            reverse("v1:token-refresh"),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # -----------------------------------------------------
    # Logout
    # -----------------------------------------------------

    def test_logout(self):

        response = self.client.post(
            reverse("v1:logout"),
            {
                "refresh": str(self.refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # -----------------------------------------------------
    # Logout Without Token
    # -----------------------------------------------------

    def test_logout_without_access_token(self):

        self.client.credentials()

        response = self.client.post(
            reverse("v1:logout"),
            {
                "refresh": str(self.refresh),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # -----------------------------------------------------
    # Invalid Logout Refresh Token
    # -----------------------------------------------------

    def test_logout_invalid_refresh_token(self):

        response = self.client.post(
            reverse("v1:logout"),
            {
                "refresh": "invalid_refresh_token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )