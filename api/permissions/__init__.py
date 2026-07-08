from .role_permissions import (
    IsAdmin,
    IsHR,
    IsManager,
    IsEmployee,
    IsAdminOrHR,
    IsAdminOrHROrManager,
    IsOwnerOrAdmin,
)

__all__ = [
    # Base role permissions
    "IsAdmin",
    "IsHR",
    "IsManager",
    "IsEmployee",
    # Composite permissions
    "IsAdminOrHR",
    "IsAdminOrHROrManager",
    # Object-level permission
    "IsOwnerOrAdmin",
]