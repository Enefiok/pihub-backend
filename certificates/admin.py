from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    # Added student_email to the display list
    list_display = ('certificate_id', 'student_name', 'student_email', 'course', 'issued_by', 'issue_date', 'is_verified')
    list_filter = ('is_verified', 'issue_date', 'course')
    
    # Changed student__username to student_email for searching
    search_fields = ('certificate_id', 'student_name', 'student_email')
    readonly_fields = ('certificate_id', 'issue_date')

    # Automatically set the 'issued_by' field to the current logged-in admin
    def save_model(self, request, obj, form, change):
        if not obj.issued_by_id:
            obj.issued_by = request.user
        super().save_model(request, obj, form, change)