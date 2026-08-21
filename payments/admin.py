from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'customer', 'booking', 'amount', 'gateway', 'status', 'created_at')
    list_filter = ('status', 'gateway', 'created_at')
    search_fields = ('transaction_id', 'customer__username', 'customer__email')
    readonly_fields = ('created_at', 'updated_at', 'gateway_response')