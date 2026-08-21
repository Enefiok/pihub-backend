from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('PIHUB Specific Info', {'fields': ('role', 'phone_number')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('PIHUB Specific Info', {'fields': ('role', 'phone_number')}),
    )