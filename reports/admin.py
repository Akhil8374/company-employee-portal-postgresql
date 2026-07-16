from django.contrib import admin
from .models import GeneratedReport


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'format', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'format', 'generated_at')
    search_fields = ('report_type', 'generated_by__username')
    readonly_fields = ('generated_at',)
    ordering = ('-generated_at',)
