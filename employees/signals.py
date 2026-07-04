import logging

from django.db.models.signals import pre_save, post_save, pre_delete, m2m_changed
from django.dispatch import receiver

from .models import Employee, EmployeeProfile

logger = logging.getLogger("application")


# ──────────────────────────────────────────────
# pre_save — Store previous salary & department
# ──────────────────────────────────────────────

@receiver(pre_save, sender=Employee)
def employee_pre_save(sender, instance, **kwargs):
    """
    Before saving an Employee:
    - If updating, store the previous salary and department
      on the instance for downstream use (e.g., audit logging).
    """
    if instance.pk:
        try:
            original = Employee.objects.get(pk=instance.pk)
            instance._previous_salary = original.salary
            instance._previous_department = original.department
            logger.info(
                "Employee %s pre_save: previous salary=%s, previous department=%s",
                instance.employee_id,
                original.salary,
                original.department,
            )
        except Employee.DoesNotExist:
            instance._previous_salary = None
            instance._previous_department = None
    else:
        instance._previous_salary = None
        instance._previous_department = None


# ──────────────────────────────────────────────
# post_save — Auto-create EmployeeProfile
# ──────────────────────────────────────────────

@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    """
    After saving an Employee:
    - If newly created, automatically create an EmployeeProfile.
    - Log the event.
    """
    if created:
        EmployeeProfile.objects.get_or_create(employee=instance)
        logger.info(
            "EmployeeProfile auto-created for %s (%s)",
            instance.employee_id,
            instance,
        )


# ──────────────────────────────────────────────
# pre_delete — Archive employee data
# ──────────────────────────────────────────────

@receiver(pre_delete, sender=Employee)
def employee_pre_delete(sender, instance, **kwargs):
    """
    Before deleting an Employee:
    - Log the archived data for audit purposes.
    """
    logger.warning(
        "Employee about to be deleted — archiving: id=%s, employee_id=%s, "
        "name=%s %s, email=%s, department=%s, salary=%s, joining_date=%s",
        instance.pk,
        instance.employee_id,
        instance.first_name,
        instance.last_name,
        instance.email,
        instance.department.name if instance.department else "N/A",
        instance.salary,
        instance.joining_date,
    )


# ──────────────────────────────────────────────
# m2m_changed — Track skill changes
# ──────────────────────────────────────────────

@receiver(m2m_changed, sender=Employee.skills.through)
def employee_skills_changed(sender, instance, action, pk_set, **kwargs):
    """
    When skills are added or removed from an Employee:
    - Log the changes.
    """
    if action == "post_add":
        from .models import Skill
        added = Skill.objects.filter(pk__in=pk_set).values_list("name", flat=True)
        logger.info(
            "Skills ADDED to %s: %s",
            instance.employee_id,
            list(added),
        )

    elif action == "post_remove":
        from .models import Skill
        removed = Skill.objects.filter(pk__in=pk_set).values_list("name", flat=True)
        logger.info(
            "Skills REMOVED from %s: %s",
            instance.employee_id,
            list(removed),
        )

    elif action == "post_clear":
        logger.info(
            "All skills CLEARED from %s",
            instance.employee_id,
        )
