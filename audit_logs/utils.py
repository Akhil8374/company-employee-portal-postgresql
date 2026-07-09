from .models import AuditLog


def create_audit_log(user=None, action="", module="", object_id=None, details=None, ip_address=None):
    """
    Reusable utility to create an audit log entry.

    Args:
        user: The User instance who performed the action (can be None for system actions).
        action: One of CREATE, UPDATE, DELETE, LOGIN, LOGOUT.
        module: One of EMPLOYEE, DEPARTMENT, AUTH.
        object_id: Primary key of the affected object (as string).
        details: Dict of additional details (e.g., changed fields).
        ip_address: IP address of the request.
    """
    return AuditLog.objects.create(
        user=user,
        action=action,
        module=module,
        object_id=str(object_id) if object_id else None,
        details=details or {},
        ip_address=ip_address,
    )


def get_client_ip(request):
    """
    Extract client IP address from the request.
    Handles proxied requests (X-Forwarded-For).
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
