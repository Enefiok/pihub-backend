from django.contrib import admin
from .models import WorkspacePlan, WorkspaceTag, Booking

@admin.register(WorkspacePlan)
class WorkspacePlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price', 'is_active', 'created_at')
    list_filter = ('is_active', 'name')
    search_fields = ('name', 'description')

@admin.register(WorkspaceTag)
class WorkspaceTagAdmin(admin.ModelAdmin):
    list_display = ('tag_code', 'is_available', 'current_booking', 'created_at')
    list_filter = ('is_available',)
    search_fields = ('tag_code',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'workspace_plan', 'status', 'payment_verified', 'start_date', 'end_date')
    list_filter = ('status', 'payment_verified', 'workspace_plan')
    search_fields = ('customer_name', 'customer_email', 'id')
    readonly_fields = ('created_at', 'updated_at')