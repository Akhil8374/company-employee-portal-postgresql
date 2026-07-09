from rest_framework.permissions import BasePermission


class IsHRorAdmin(BasePermission):
    """
    Only HR and Admin can upload/delete documents.
    Employees can only view documents.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.role in ["ADMIN", "HR"]