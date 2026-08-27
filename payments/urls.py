from django.urls import path
from .views import paystack_webhook

urlpatterns = [
    # The Webhook Endpoint (No authentication required, secured by signature in production)
    path('webhook/paystack/', paystack_webhook, name='paystack-webhook'),
]