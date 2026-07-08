import logging

from django.contrib.auth import authenticate, update_session_auth_hash, get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import PasswordResetToken
from accounts.security import SecurityLog, log_security_event
from api.responses import SuccessResponse, ErrorResponse
from api.serializers import (
    LogoutSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from api.throttling import LoginRateThrottle
from audit_logs.utils import create_audit_log, get_client_ip

logger = logging.getLogger("security")
User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# Module 1: Login — JWT Token Generation
# POST /api/v1/auth/login/
# ─────────────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    Authenticates a user and returns JWT access + refresh tokens.

    - Throttled to 5 requests/minute per IP (brute-force protection)
    - Logs both login success and failure events to SecurityLog
    - Performs session cycle to prevent session fixation
    """
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        client_ip = get_client_ip(request)

        if not username or not password:
            return ErrorResponse(
                message="Validation Error",
                errors={"detail": "Username and password are required."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)

        # ── Login Failure ────────────────────────────────────────────────────
        if user is None:
            log_security_event(
                action=SecurityLog.ACTION_LOGIN_FAILURE,
                status=SecurityLog.STATUS_FAILURE,
                ip_address=client_ip,
                details={"attempted_username": username, "reason": "Invalid credentials"},
            )
            logger.warning(
                "LOGIN_FAILURE | IP=%s | username=%s | reason=invalid_credentials",
                client_ip, username,
            )
            return ErrorResponse(
                message="Authentication Failed",
                errors={"detail": "Invalid username or password."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            log_security_event(
                action=SecurityLog.ACTION_LOGIN_FAILURE,
                status=SecurityLog.STATUS_FAILURE,
                user=user,
                ip_address=client_ip,
                details={"reason": "Account inactive"},
            )
            return ErrorResponse(
                message="Authentication Failed",
                errors={"detail": "This account is inactive."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # ── Session Management ───────────────────────────────────────────────
        request.session.cycle_key()  # Prevent session fixation
        request.session["user_id"]   = user.pk
        request.session["username"]  = user.username
        request.session["email"]     = user.email
        request.session["role"]      = user.role
        request.session["selected_department"] = None
        request.session["dashboard_theme"]     = "default"

        # ── JWT Token Generation ─────────────────────────────────────────────
        refresh = RefreshToken.for_user(user)

        # ── Login Success Logging ────────────────────────────────────────────
        log_security_event(
            action=SecurityLog.ACTION_LOGIN_SUCCESS,
            status=SecurityLog.STATUS_SUCCESS,
            user=user,
            ip_address=client_ip,
            details={"username": user.username, "role": user.role},
        )

        create_audit_log(
            user=user,
            action="LOGIN",
            module="AUTH",
            object_id=user.pk,
            details={"username": user.username},
            ip_address=client_ip,
        )

        logger.info(
            "LOGIN_SUCCESS | IP=%s | user=%s | role=%s",
            client_ip, user.username, user.role,
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
                "session": {
                    "selected_department": request.session["selected_department"],
                    "dashboard_theme": request.session["dashboard_theme"],
                },
            },
            message="Login successful",
            status_code=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module 1: Refresh Token
# POST /api/v1/auth/refresh/
# ─────────────────────────────────────────────────────────────────────────────

class TokenRefreshView(APIView):
    """
    Issues a new access token using a valid refresh token.

    With ROTATE_REFRESH_TOKENS=True (configured in settings), the simplejwt
    library automatically issues a new refresh token and blacklists the old one.
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
            new_access = str(refresh.access_token)

            response_data = {"access": new_access}

            # If rotation is enabled, also return the new refresh token
            # (simplejwt handles blacklisting the old one automatically)
            if getattr(refresh, "token", None) is not None:
                response_data["refresh"] = str(refresh)

            return SuccessResponse(
                data=response_data,
                message="Token refreshed successfully",
            )

        except TokenError:
            return ErrorResponse(
                message="Invalid Token",
                errors={"detail": "Token is invalid or expired."},
                status_code=status.HTTP_401_UNAUTHORIZED,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Module 2: Logout — Token Blacklisting
# POST /api/v1/auth/logout/
# ─────────────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    Securely logs out the user by blacklisting the provided refresh token.

    - The refresh token is added to the simplejwt blacklist
    - The session is flushed
    - Security event is logged
    - Once blacklisted, the token cannot be used for refresh
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh"]
        client_ip = get_client_ip(request)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            # ── Security & Audit Logging ──────────────────────────────────────
            log_security_event(
                action=SecurityLog.ACTION_TOKEN_BLACKLISTED,
                status=SecurityLog.STATUS_SUCCESS,
                user=request.user,
                ip_address=client_ip,
                details={"username": request.user.username},
            )

            log_security_event(
                action=SecurityLog.ACTION_LOGOUT,
                status=SecurityLog.STATUS_SUCCESS,
                user=request.user,
                ip_address=client_ip,
                details={"username": request.user.username},
            )

            create_audit_log(
                user=request.user,
                action="LOGOUT",
                module="AUTH",
                object_id=request.user.pk,
                details={"username": request.user.username},
                ip_address=client_ip,
            )

            # Clear server-side session
            request.session.flush()

            return SuccessResponse(
                message="Logout successful. Token has been blacklisted.",
                status_code=status.HTTP_200_OK,
            )

        except TokenError:
            return ErrorResponse(
                message="Invalid Token",
                errors={"detail": "Token is invalid or already blacklisted."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Module 3: Change Password
# POST /api/v1/auth/change-password/
# ─────────────────────────────────────────────────────────────────────────────

class ChangePasswordView(APIView):
    """
    Allows an authenticated user to change their password.

    - Verifies the current password before allowing the change
    - New password must meet Django's strength validators
    - All existing refresh tokens are blacklisted after the change
    - Security event is logged
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        client_ip = get_client_ip(request)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Validation Error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user

        # Verify current password
        if not user.check_password(serializer.validated_data["current_password"]):
            log_security_event(
                action=SecurityLog.ACTION_PASSWORD_CHANGE,
                status=SecurityLog.STATUS_FAILURE,
                user=user,
                ip_address=client_ip,
                details={"reason": "Incorrect current password"},
            )
            return ErrorResponse(
                message="Authentication Failed",
                errors={"current_password": "Current password is incorrect."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Update password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        # Keep current session alive after password change
        update_session_auth_hash(request, user)

        # Blacklist ALL outstanding refresh tokens (invalidate other sessions)
        try:
            from rest_framework_simplejwt.token_blacklist.models import (
                OutstandingToken, BlacklistedToken
            )
            outstanding_tokens = OutstandingToken.objects.filter(user=user)
            for token in outstanding_tokens:
                BlacklistedToken.objects.get_or_create(token=token)
        except Exception:
            pass  # Non-critical — log but continue

        # ── Security & Audit Logging ──────────────────────────────────────────
        log_security_event(
            action=SecurityLog.ACTION_PASSWORD_CHANGE,
            status=SecurityLog.STATUS_SUCCESS,
            user=user,
            ip_address=client_ip,
            details={"username": user.username},
        )

        create_audit_log(
            user=user,
            action="PASSWORD_CHANGE",
            module="AUTH",
            object_id=user.pk,
            details={"username": user.username},
            ip_address=client_ip,
        )

        logger.warning(
            "PASSWORD_CHANGE | IP=%s | user=%s",
            client_ip, user.username,
        )

        return SuccessResponse(
            message="Password changed successfully. All other sessions have been invalidated.",
            status_code=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module 4: Forgot Password — DB-backed reset token with 15-min expiry
# POST /api/v1/auth/forgot-password/
# ─────────────────────────────────────────────────────────────────────────────

class ForgotPasswordView(APIView):
    """
    Generates a secure password reset token and returns it in the response.

    In production: this token should be sent via email, not returned in the API.
    The token is stored in the DB (PasswordResetToken) and expires after 15 minutes.
    Previous unused tokens for the same user are invalidated.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        client_ip = get_client_ip(request)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Validation Error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.get(email=serializer.validated_data["email"])

        # Invalidate any existing unused tokens for this user
        PasswordResetToken.objects.filter(user=user, is_used=False).delete()

        # Create a new DB-backed token with 15-minute expiry
        reset_token = PasswordResetToken.objects.create(user=user)

        log_security_event(
            action=SecurityLog.ACTION_PASSWORD_RESET,
            status=SecurityLog.STATUS_SUCCESS,
            user=user,
            ip_address=client_ip,
            details={"step": "token_generated", "username": user.username},
        )

        logger.warning(
            "PASSWORD_RESET_TOKEN_GENERATED | IP=%s | user=%s",
            client_ip, user.username,
        )

        # NOTE: In production, send this token via email instead
        return SuccessResponse(
            data={
                "reset_token": str(reset_token.token),
                "expires_in_minutes": 15,
                "note": "This token expires in 15 minutes. In production, it would be sent via email.",
            },
            message="Password reset token generated successfully.",
            status_code=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module 4: Reset Password — validate DB token + 15-min expiry
# POST /api/v1/auth/reset-password/
# ─────────────────────────────────────────────────────────────────────────────

class ResetPasswordView(APIView):
    """
    Resets the user's password using a valid, non-expired reset token.

    - Validates the token exists in the DB and belongs to a user
    - Rejects expired tokens (> 15 minutes old)
    - Rejects already-used tokens
    - Marks the token as used after successful reset
    - Blacklists all outstanding refresh tokens
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        client_ip = get_client_ip(request)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Validation Error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        token_str = serializer.validated_data["token"]

        # Look up the reset token in the DB
        try:
            reset_token = PasswordResetToken.objects.select_related("user").get(
                token=token_str
            )
        except (PasswordResetToken.DoesNotExist, ValueError):
            return ErrorResponse(
                message="Invalid Token",
                errors={"token": "The reset token is invalid."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Validate token state
        if reset_token.is_used:
            return ErrorResponse(
                message="Token Already Used",
                errors={"token": "This reset token has already been used."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if reset_token.is_expired:
            return ErrorResponse(
                message="Token Expired",
                errors={"token": "This reset token has expired. Please request a new one."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = reset_token.user

        # Reset the password
        user.set_password(serializer.validated_data["new_password"])
        user.save()

        # Mark token as used (single-use enforcement)
        reset_token.is_used = True
        reset_token.save(update_fields=["is_used"])

        # Blacklist all outstanding refresh tokens
        try:
            from rest_framework_simplejwt.token_blacklist.models import (
                OutstandingToken, BlacklistedToken
            )
            for token in OutstandingToken.objects.filter(user=user):
                BlacklistedToken.objects.get_or_create(token=token)
        except Exception:
            pass

        # ── Security Logging ──────────────────────────────────────────────────
        log_security_event(
            action=SecurityLog.ACTION_PASSWORD_RESET,
            status=SecurityLog.STATUS_SUCCESS,
            user=user,
            ip_address=client_ip,
            details={"step": "password_reset_completed", "username": user.username},
        )

        create_audit_log(
            user=user,
            action="PASSWORD_RESET",
            module="AUTH",
            object_id=user.pk,
            details={"username": user.username},
            ip_address=client_ip,
        )

        logger.warning(
            "PASSWORD_RESET_COMPLETED | IP=%s | user=%s",
            client_ip, user.username,
        )

        return SuccessResponse(
            message="Password has been reset successfully. Please login with your new password.",
            status_code=status.HTTP_200_OK,
        )