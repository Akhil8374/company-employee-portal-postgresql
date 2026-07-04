from django.db import models
from django.utils import timezone
from .querysets import EmployeeQuerySet


class EmployeeManager(models.Manager):

    def get_queryset(self):
        return EmployeeQuerySet(
            self.model,
            using=self._db,
        )

    def active_employees(self):
        return self.get_queryset().active()

    def inactive_employees(self):
        return self.get_queryset().inactive()

    def highest_salary(self):
        return self.get_queryset().order_by("-salary")

    def new_joiners(self):
        return self.get_queryset().new_joiners()