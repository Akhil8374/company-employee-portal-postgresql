from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from api.responses import SuccessResponse, ErrorResponse
from api.permissions import IsOwnerOrAdmin
from api.serializers import UserSerializer
from accounts.validators import SecureImageValidator
from accounts.security import SecurityLog, log_security_event
from audit_logs.utils import create_audit_log, get_client_ip


# ─────────────────────────────────────────────────────────────────────────────
# Module 6: My Profile — Object-Level Permission (self-only)
# GET /api/v1/profile/
# ─────────────────────────────────────────────────────────────────────────────

class MyProfileView(APIView):
    """
    Returns the authenticated user's own profile.

    Object-Level Permission (Module 6):
      - An Employee can ONLY access their own profile via GET /api/v1/profile/
      - They CANNOT access /api/v1/employees/15/ (blocked by IsAdminOrHR on that view)
      - Admin can still view any profile via this endpoint (IsOwnerOrAdmin)

    This enforces the requirement: employees see only their own data.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get(self, request):
        user = request.user

        # Object-level permission check — user can only access their own object
        self.check_object_permissions(request, user)

        serializer = UserSerializer(user)

        return SuccessResponse(
            data=serializer.data,
            message="Profile retrieved successfully",
            status_code=status.HTTP_200_OK,
        )

    def put(self, request):
        """Allow users to update their own profile (non-sensitive fields only)."""
        user = request.user
        self.check_object_permissions(request, user)

        # Only allow safe fields to be updated via profile endpoint
        UPDATABLE_FIELDS = {"first_name", "last_name", "phone"}
        data = {k: v for k, v in request.data.items() if k in UPDATABLE_FIELDS}

        serializer = UserSerializer(user, data=data, partial=True)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Validation Error",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        create_audit_log(
            user=user,
            action="UPDATE",
            module="AUTH",
            object_id=user.pk,
            details={"updated_fields": list(data.keys())},
            ip_address=get_client_ip(request),
        )

        return SuccessResponse(
            data=serializer.data,
            message="Profile updated successfully",
            status_code=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Module 8: Profile Image Upload — Secure File Upload
# POST /api/v1/profile/image/
# ─────────────────────────────────────────────────────────────────────────────

class ProfileImageUploadView(APIView):
    """
    Securely uploads or updates a user's profile image.

    Module 8 — Security Validation:
      - Accepts ONLY .jpg / .jpeg / .png files
      - Maximum file size: 2 MB
      - Validates true MIME type (not just extension) to detect disguised uploads
      - Rejects: .exe, .zip, .js, .bat, .sh, .cmd, .msi, .dll, etc.

    Only the authenticated user can upload their own profile image.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        client_ip = get_client_ip(request)

        if "profile_image" not in request.FILES:
            return ErrorResponse(
                message="Validation Error",
                errors={"profile_image": "No image file was provided."},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        image_file = request.FILES["profile_image"]

        # Run security validation
        validator = SecureImageValidator()
        try:
            validator(image_file)
        except Exception as e:
            log_security_event(
                action=SecurityLog.ACTION_UNAUTHORIZED,
                status=SecurityLog.STATUS_FAILURE,
                user=request.user,
                ip_address=client_ip,
                details={
                    "reason": "Rejected file upload",
                    "filename": image_file.name,
                    "error": str(e),
                },
            )
            return ErrorResponse(
                message="File Upload Rejected",
                errors={"profile_image": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.profile_image = image_file
        user.save(update_fields=["profile_image"])

        create_audit_log(
            user=user,
            action="UPDATE",
            module="AUTH",
            object_id=user.pk,
            details={"updated_fields": ["profile_image"], "filename": image_file.name},
            ip_address=client_ip,
        )

        return SuccessResponse(
            data={
                "profile_image": request.build_absolute_uri(user.profile_image.url)
                if user.profile_image else None,
            },
            message="Profile image uploaded successfully.",
            status_code=status.HTTP_200_OK,
        )
