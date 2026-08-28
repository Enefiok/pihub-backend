from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Subscriber, Newsletter, GalleryImage, Enquiry

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at', 'unsubscribe_link')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)

    def unsubscribe_link(self, obj):
        url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/unsubscribe/{obj.unsubscribe_token}/"
        return format_html('<a href="{}" target="_blank">Unsubscribe</a>', url)
    unsubscribe_link.short_description = 'Unsubscribe Link'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'is_sent', 'sent_at', 'created_at')
    list_filter = ('is_sent', 'created_at')
    search_fields = ('subject',)
    actions = ['send_newsletter_action']
    readonly_fields = ('is_sent', 'sent_at')

    @admin.action(description="📧 Send selected newsletters to active subscribers")
    def send_newsletter_action(self, request, queryset):
        count = 0
        for newsletter in queryset.filter(is_sent=False):
            try:
                sent_count = newsletter.send()
                count += 1
                self.message_user(request, f"Newsletter '{newsletter.subject}' sent to {sent_count} subscribers.")
            except Exception as e:
                self.message_user(request, f"Failed to send '{newsletter.subject}': {str(e)}", level='ERROR')
        
        if count == 0:
            self.message_user(request, "No unsent newsletters were selected.", level='WARNING')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'display_order', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    list_editable = ('display_order', 'is_active')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'service_type', 'status', 'created_at')
    list_filter = ('service_type', 'status')
    search_fields = ('name', 'email', 'subject', 'message')