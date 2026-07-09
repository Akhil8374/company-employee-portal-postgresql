from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate

from api.responses import SuccessResponse, ErrorResponse
from api.serializers import LogoutSerializer
from api.throttling import LoginRateThrottle
from audit_logs.utils import create_audit_log, get_client_ip


class LoginView(APIView):
    """
    POST /api/v1/auth/login/
    JWT Login — returns access + refresh tokens in company standard format.
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return ErrorResponse(
                message="Validation Error",
                errors={"detail": "Username and password are required."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)

        if user is None:
            return ErrorResponse(
                message="Authentication Failed",
                errors={"detail": "Invalid username or password."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return ErrorResponse(
                message="Authentication Failed",
                errors={"detail": "This account is inactive."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Audit log
        create_audit_log(
            user=user,
            action="LOGIN",
            module="AUTH",
            object_id=user.pk,
            details={"username": user.username},
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.pk,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                },
            },
            message="Login successful",
            status_code=status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    """
    POST /api/v1/auth/refresh/
    Refresh JWT access token — wraps response in company standard format.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return ErrorResponse(
                message="Validation Error",
                errors={"refresh": "Refresh token is required."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            return SuccessResponse(
                data={
                    "access": str(refresh.access_token),
                },
                message="Token refreshed successfully",
            )
        except TokenError:
            return ErrorResponse(
                message="Invalid Token",
                errors={"detail": "Token is invalid or expired."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Blacklists the refresh token to log the user out.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Audit log
            create_audit_log(
                user=request.user,
                action="LOGOUT",
                module="AUTH",
                object_id=request.user.pk,
                details={"username": request.user.username},
                ip_address=get_client_ip(request),
            )

            return SuccessResponse(
                message="Logout successful",
                status_code=status.HTTP_200_OK,
            )
        except TokenError:
            return ErrorResponse(
                message="Invalid Token",
                errors={"detail": "Token is invalid or already blacklisted."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
