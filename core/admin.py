from django.contrib import admin
from .models import GalleryImage, Enquiry

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'is_active', 'display_order', 'created_at')
    list_filter = ('section', 'is_active')
    search_fields = ('title', 'caption')

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'service_interest', 'is_read', 'created_at')
    list_filter = ('service_interest', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)