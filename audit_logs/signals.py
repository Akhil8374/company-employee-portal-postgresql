from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from employees.models import Employee
from .utils import create_audit_log


@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    """
    Signal: After Employee is saved.
    - On create: log CREATE action
    - On update: log UPDATE action
    """
    if created:
        create_audit_log(
            user=None,  # Will be set by the view via service layer
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
        create_audit_log(
            user=None,
            action="UPDATE",
            module="EMPLOYEE",
            object_id=instance.pk,
            details={
                "employee_id": instance.employee_id,
                "name": f"{instance.first_name} {instance.last_name}",
            },
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
