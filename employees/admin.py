from django.contrib import admin
from .models import (
    Employee,
    Department,
    Skill,
    EmployeeProfile,
    Payroll,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "blood_group",
        "emergency_contact",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):

    list_display = (
        "employee",
        "amount",
        "status",
        "processed_on",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
    )

    list_filter = (
        "status",
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "salary",
        "department",
        "designation",
        "status",
    )

    search_fields = (
        "employee_id",
        "first_name",
        "last_name",
        "email",
    )

    list_filter = (
        "department",
        "status",
    )

    filter_horizontal = (
        "skills",
    )