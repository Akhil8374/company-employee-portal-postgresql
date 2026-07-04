from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from employees.models import Employee, Department
from .utils import create_audit_log


# ──────────────────────────────────────────────
# Employee Signals
# ──────────────────────────────────────────────

@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    """
    Signal: After Employee is saved.
    - On create: log CREATE action
    - On update: log UPDATE action with previous values
    """
    if created:
        create_audit_log(
            user=None,
            action="CREATE",
            module="EMPLOYEE",
            object_id=instance.pk,
            details={
                "employee_id": instance.employee_id,
                "name": f"{instance.first_name} {instance.last_name}",
                "email": instance.email,
                "department": instance.department.name if instance.department else None,
            },
        )
    else:
        details = {
            "employee_id": instance.employee_id,
            "name": f"{instance.first_name} {instance.last_name}",
        }

        # Include previous values if available (set by employees/signals.py pre_save)
        if hasattr(instance, "_previous_salary") and instance._previous_salary is not None:
            details["previous_salary"] = str(instance._previous_salary)
            details["new_salary"] = str(instance.salary)

        if hasattr(instance, "_previous_department") and instance._previous_department is not None:
            details["previous_department"] = instance._previous_department.name
            details["new_department"] = instance.department.name if instance.department else None

        create_audit_log(
            user=None,
            action="UPDATE",
            module="EMPLOYEE",
            object_id=instance.pk,
            details=details,
        )


@receiver(post_delete, sender=Employee)
def employee_post_delete(sender, instance, **kwargs):
    """
    Signal: After Employee is deleted.
    Stores a history record of the deleted employee.
    """
    create_audit_log(
        user=None,
        action="DELETE",
        module="EMPLOYEE",
        object_id=instance.pk,
        details={
            "employee_id": instance.employee_id,
            "name": f"{instance.first_name} {instance.last_name}",
            "email": instance.email,
            "department": instance.department.name if instance.department else None,
            "salary": str(instance.salary),
            "joining_date": str(instance.joining_date),
        },
    )


# ──────────────────────────────────────────────
# Department Signals
# ──────────────────────────────────────────────

@receiver(post_save, sender=Department)
def department_post_save(sender, instance, created, **kwargs):
    """
    Signal: After Department is saved.
    - On create: log CREATE action
    - On update: log UPDATE action
    """
    action = "CREATE" if created else "UPDATE"
    create_audit_log(
        user=None,
        action=action,
        module="DEPARTMENT",
        object_id=instance.pk,
        details={
            "name": instance.name,
            "description": instance.description[:100] if instance.description else "",
        },
    )


@receiver(post_delete, sender=Department)
def department_post_delete(sender, instance, **kwargs):
    """Signal: After Department is deleted."""
    create_audit_log(
        user=None,
        action="DELETE",
        module="DEPARTMENT",
        object_id=instance.pk,
        details={
            "name": instance.name,
        },
    )


# ──────────────────────────────────────────────
# Authentication Signals
# ──────────────────────────────────────────────

@receiver(user_logged_in)
def user_login_handler(sender, request, user, **kwargs):
    """Signal: After user logs in — log LOGIN action."""
    from .utils import get_client_ip

    create_audit_log(
        user=user,
        action="LOGIN",
        module="AUTH",
        object_id=user.pk,
        details={"username": user.username},
        ip_address=get_client_ip(request) if request else None,
    )


@receiver(user_logged_out)
def user_logout_handler(sender, request, user, **kwargs):
    """Signal: After user logs out — log LOGOUT action."""
    from .utils import get_client_ip

    create_audit_log(
        user=user,
        action="LOGOUT",
        module="AUTH",
        object_id=user.pk if user else None,
        details={"username": user.username if user else "unknown"},
        ip_address=get_client_ip(request) if request else None,
    )
