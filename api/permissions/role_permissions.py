from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only users with ADMIN role."""
    message = "Admin access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
        )


class IsHROrAdmin(BasePermission):
    """Only users with HR or ADMIN role."""
    message = "HR or Admin access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("ADMIN", "HR")
        )


class IsManagerOrAbove(BasePermission):
    """Only users with MANAGER, HR, or ADMIN role."""
    message = "Manager, HR, or Admin access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("ADMIN", "HR", "MANAGER")
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: user is the resource owner or an ADMIN.
    Requires the object to have a 'user' attribute or
    the view to define get_owner_field().
    """
    message = "You can only access your own resources."

    def has_object_permission(self, request, view, obj):
        if request.user.role == "ADMIN":
            return True

        # Check if the object has a user/owner field
        owner_field = getattr(view, "owner_field", "user")
        owner = getattr(obj, owner_field, None)

        if owner and hasattr(owner, "pk"):
            return owner.pk == request.user.pk
        return False
