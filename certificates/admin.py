from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student_name', 'course', 'issue_date', 'is_verified')
    list_filter = ('is_verified', 'issue_date', 'course')
    search_fields = ('certificate_id', 'student_name', 'student__username')
    readonly_fields = ('certificate_id', 'issue_date')