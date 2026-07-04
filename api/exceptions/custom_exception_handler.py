from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    Throttled,
    APIException,
)
from rest_framework.views import exception_handler
from django.http import Http404

from api.responses import ErrorResponse


def custom_exception_handler(exc, context):
    """
    Global exception handler for Django REST Framework.

    Converts all exceptions into the company standard error format:
    {
        "success": false,
        "message": "...",
        "errors": { ... }
    }
    """

    # Let DRF handle the exception first to get standard behavior
    # (e.g., setting response headers, handling 403 vs 401 logic)
    response = exception_handler(exc, context)

    # --- Validation Errors ---
    if isinstance(exc, ValidationError):
        errors = _flatten_validation_errors(exc.detail)
        return ErrorResponse(
            message="Validation Error",
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # --- Authentication Errors ---
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        message = (
            str(exc.detail)
            if hasattr(exc, "detail")
            else "Authentication credentials were not provided."
        )
        return ErrorResponse(
            message=message,
            errors={"detail": message},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # --- Permission Errors ---
    if isinstance(exc, PermissionDenied):
        message = (
            str(exc.detail)
            if hasattr(exc, "detail")
            else "You do not have permission to perform this action."
        )
        return ErrorResponse(
            message=message,
            errors={"detail": message},
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # --- Not Found Errors ---
    if isinstance(exc, (NotFound, Http404)):
        message = "Resource not found."
        if isinstance(exc, NotFound) and hasattr(exc, "detail"):
            message = str(exc.detail)
        return ErrorResponse(
            message=message,
            errors={"detail": message},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # --- Method Not Allowed ---
    if isinstance(exc, MethodNotAllowed):
        message = str(exc.detail) if hasattr(exc, "detail") else "Method not allowed."
        return ErrorResponse(
            message=message,
            errors={"detail": message},
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    # --- Throttled ---
    if isinstance(exc, Throttled):
        wait = exc.wait
        message = f"Request was throttled. Expected available in {int(wait)} seconds."
        return ErrorResponse(
            message=message,
            errors={"detail": message},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # --- Other DRF API Exceptions ---
    if isinstance(exc, APIException):
        message = str(exc.detail) if hasattr(exc, "detail") else "An error occurred."
        return ErrorResponse(
            message=message,
            errors={"detail": message},
            status_code=exc.status_code,
        )

    # --- Unhandled Server Errors (500) ---
    if response is None:
        return ErrorResponse(
            message="Internal Server Error",
            errors={"detail": "An unexpected error occurred. Please try again later."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _flatten_validation_errors(detail):
    """
    Flatten DRF validation error detail into a clean dictionary.

    DRF returns errors like: {"email": ["Already exists"]}
    We convert to:          {"email": "Already exists"}

    For nested errors or lists, we keep them as-is.
    """
    if isinstance(detail, list):
        # Top-level list of errors (non_field_errors)
        return {"non_field_errors": detail[0] if len(detail) == 1 else detail}

    if isinstance(detail, dict):
        errors = {}
        for field, messages in detail.items():
            if isinstance(messages, list):
                # Take first error message per field for clean output
                errors[field] = str(messages[0]) if len(messages) == 1 else [str(m) for m in messages]
            elif isinstance(messages, dict):
                # Nested serializer errors — recurse
                errors[field] = _flatten_validation_errors(messages)
            else:
                errors[field] = str(messages)
        return errors

    return {"detail": str(detail)}
