from django.urls import path
from .views import paystack_webhook, initialize_payment, PaymentListView

urlpatterns = [
    # List all payments (GET /api/payments/)
    path('', PaymentListView.as_view(), name='payment-list'),
    
    # The Initialize Payment Endpoint (Called by Frontend/Postman)
    path('initialize/', initialize_payment, name='initialize-payment'),
    
    # The Webhook Endpoint (No authentication required, secured by signature in production)
    path('webhook/paystack/', paystack_webhook, name='paystack-webhook'),
]