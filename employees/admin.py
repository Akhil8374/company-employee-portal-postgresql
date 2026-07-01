import csv
from django.contrib import admin
from django.http import HttpResponse
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

    date_hierarchy = "joining_date"
    readonly_fields = ("employee_id", "created_at", "updated_at")

    actions = ["mark_active", "mark_inactive", "export_csv"]

    @admin.action(description="Mark selected employees as active")
    def mark_active(self, request, queryset):
        updated = queryset.update(status=True)
        self.message_user(request, f"{updated} employees successfully marked as active.")

    @admin.action(description="Mark selected employees as inactive")
    def mark_inactive(self, request, queryset):
        updated = queryset.update(status=False)
        self.message_user(request, f"{updated} employees successfully marked as inactive.")

    @admin.action(description="Export selected employees to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="employees.csv"'

        writer = csv.writer(response)
        writer.writerow(["Employee ID", "First Name", "Last Name", "Email", "Salary", "Department", "Designation", "Status", "Joining Date"])

        for emp in queryset:
            writer.writerow([
                emp.employee_id,
                emp.first_name,
                emp.last_name,
                emp.email,
                emp.salary,
                emp.department.name if emp.department else "",
                emp.designation,
                "Active" if emp.status else "Inactive",
                emp.joining_date
            ])

        return response