from django.db.models import (
    Q,
    F,
    Count,
    Sum,
    Avg,
    Max,
    Min,
    DecimalField,
    ExpressionWrapper,
)
from django.utils import timezone

from employees.models import Employee


class EmployeeRepository:

    @staticmethod
    def get_all():
        return (
            Employee.objects
            .select_related("department", "manager")
            .prefetch_related("skills")
            .all()
        )

    @staticmethod
    def get_by_id(pk):
        try:
            return (
                Employee.objects
                .select_related("department", "manager")
                .prefetch_related("skills")
                .get(pk=pk)
            )
        except Employee.DoesNotExist:
            return None

    @staticmethod
    def create(validated_data):
        return Employee.objects.create(**validated_data)

    @staticmethod
    def update(instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def delete(instance):
        instance.delete()

    @staticmethod
    def get_by_department(department_id):
        return (
            Employee.objects
            .select_related("department")
            .prefetch_related("skills")
            .filter(department_id=department_id)
        )

    @staticmethod
    def get_optimized_list():
        return (
            Employee.objects
            .select_related("department", "manager")
            .prefetch_related("skills")
            .only(
                "id",
                "employee_id",
                "first_name",
                "last_name",
                "email",
                "designation",
                "salary",
                "joining_date",
                "status",
                "department__id",
                "department__name",
            )
            .defer("profile_image")
        )

    @staticmethod
    def filter_queryset(queryset, filters):

        if filters.get("department"):
            queryset = queryset.filter(
                department_id=filters["department"]
            )

        if filters.get("status") is not None:
            queryset = queryset.filter(
                status=filters["status"]
            )

        if filters.get("min_salary"):
            queryset = queryset.filter(
                salary__gte=filters["min_salary"]
            )

        if filters.get("max_salary"):
            queryset = queryset.filter(
                salary__lte=filters["max_salary"]
            )

        if filters.get("designation"):
            queryset = queryset.filter(
                designation__icontains=filters["designation"]
            )

        if filters.get("search"):
            keyword = filters["search"]

            queryset = queryset.filter(
                Q(first_name__icontains=keyword)
                | Q(last_name__icontains=keyword)
                | Q(employee_id__icontains=keyword)
                | Q(email__icontains=keyword)
            )

        if filters.get("exclude_department"):
            queryset = queryset.exclude(
                department_id=filters["exclude_department"]
            )

        return queryset

    @staticmethod
    def top_10_highest_paid():
        return (
            Employee.objects
            .select_related("department")
            .order_by("-salary")[:10]
        )

    @staticmethod
    def department_employee_count():
        return (
            Employee.objects
            .values("department__name")
            .annotate(employee_count=Count("id"))
            .order_by("department__name")
        )

    @staticmethod
    def monthly_salary_statistics():
        return Employee.objects.aggregate(
            total_salary=Sum("salary"),
            average_salary=Avg("salary"),
            highest_salary=Max("salary"),
            lowest_salary=Min("salary"),
        )

    @staticmethod
    def employees_joined_this_month():

        today = timezone.now().date()

        return Employee.objects.filter(
            joining_date__year=today.year,
            joining_date__month=today.month,
        )

    @staticmethod
    def increase_salary_by_percentage(percentage=10):

        multiplier = 1 + (percentage / 100)

        return Employee.objects.update(
            salary=ExpressionWrapper(
                F("salary") * multiplier,
                output_field=DecimalField(
                    max_digits=10,
                    decimal_places=2,
                ),
            )
        )