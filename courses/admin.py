from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'duration', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'enrolled_at')
    search_fields = ('student__username', 'student__email')