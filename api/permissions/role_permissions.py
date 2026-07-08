from rest_framework.permissions import BasePermission


# ─────────────────────────────────────────────────────────────────────────────
# Base Role Permissions (Module 5)
# ─────────────────────────────────────────────────────────────────────────────

class IsAdmin(BasePermission):
    """
    Grants access only to Admin role users.
    Use for: Reports, system-wide settings, user management.
    """
    message = "Access denied. Admin role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "ADMIN"
        )


class IsHR(BasePermission):
    """
    Grants access only to HR role users.
    Use for: Employee CRUD, payroll management, onboarding.
    """
    message = "Access denied. HR role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "HR"
        )


class IsManager(BasePermission):
    """
    Grants access only to Manager role users.
    Use for: Analytics, team dashboards, subordinate data.
    """
    message = "Access denied. Manager role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "MANAGER"
        )


class IsEmployee(BasePermission):
    """
    Grants access only to Employee role users.
    Use for: Own profile access, attendance, payslip.
    """
    message = "Access denied. Employee role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "EMPLOYEE"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Composite Role Permissions
# ─────────────────────────────────────────────────────────────────────────────

class IsAdminOrHR(BasePermission):
    """
    Grants access to Admin OR HR users.
    Use for: Employee list/detail, department management.
    """
    message = "Access denied. Admin or HR role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ("ADMIN", "HR")
        )


class IsAdminOrHROrManager(BasePermission):
    """
    Grants access to Admin, HR, or Manager users.
    Use for: Dashboard, analytics, reporting views.
    """
    message = "Access denied. Admin, HR, or Manager role required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ("ADMIN", "HR", "MANAGER")
        )


# ─────────────────────────────────────────────────────────────────────────────
# Object-Level Permission (Module 6)
# ─────────────────────────────────────────────────────────────────────────────

class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: grants access if the requesting user is the
    object's owner OR has Admin role.

    The view must pass the object to `has_object_permission()`.
    The object must have a `user` attribute or `pk` to compare against request.user.

    Example usage:
        permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        ...
        self.check_object_permissions(request, user_object)
    """
    message = "Access denied. You can only access your own resources."

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.role == "ADMIN":
            return True

        # Owner check — object is a User instance
        if hasattr(obj, "pk") and obj.pk == request.user.pk:
            return True

        # Owner check — object has a user FK
        if hasattr(obj, "user") and obj.user == request.user:
            return True

        return False