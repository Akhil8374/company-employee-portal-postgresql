from django.db import models
from django.utils import timezone


class EmployeeQuerySet(models.QuerySet):

    def active(self):
        return self.filter(status=True)

    def inactive(self):
        return self.filter(status=False)

    def engineering(self):
        return self.filter(
            department__name__iexact="Engineering"
        )

    def high_salary(self):
        return self.filter(
            salary__gte=100000
        )

    def new_joiners(self):
        today = timezone.now().date()

        return self.filter(
            joining_date__year=today.year,
            joining_date__month=today.month,
        )