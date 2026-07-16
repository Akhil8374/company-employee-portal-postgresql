from django.db import models
from django.conf import settings


class GeneratedReport(models.Model):
    """
    Stores generated report files so they can be downloaded later by ID.
    Supports Excel, PDF, and CSV formats for every report type.
    """

    REPORT_TYPES = [
        ("employee", "Employee Report"),
        ("department", "Department Report"),
        ("salary", "Salary Report"),
        ("attendance", "Attendance Report"),
        ("dashboard", "Dashboard Report"),
    ]

    FORMAT_CHOICES = [
        ("excel", "Excel (.xlsx)"),
        ("pdf", "PDF (.pdf)"),
        ("csv", "CSV (.csv)"),
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file = models.FileField(upload_to="reports/")
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="generated_reports",
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.get_report_type_display()} ({self.format}) — {self.generated_at:%Y-%m-%d %H:%M}"
