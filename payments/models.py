from django.db import models
from accounts.models import User
from workspaces.models import Booking

class Payment(models.Model):
    """
    Tracks payment transactions for bookings.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    class Gateway(models.TextChoices):
        PAYSTACK = 'PAYSTACK', 'Paystack'
        FLUTTERWAVE = 'FLUTTERWAVE', 'Flutterwave'
        MANUAL = 'MANUAL', 'Manual (Receptionist)'

    booking = models.ForeignKey(
        Booking, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payments'
    )
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    gateway = models.CharField(max_length=20, choices=Gateway.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Gateway specific references
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    gateway_response = models.JSONField(blank=True, null=True, help_text="Raw response from payment gateway")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.transaction_id or 'Pending'} - {self.status}"