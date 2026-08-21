from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User

class WorkspacePlan(models.Model):
    """
    Workspace plans as per Section 6.1
    """
    class PlanType(models.TextChoices):
        DAILY = 'DAILY', 'Daily'
        WEEKLY = 'WEEKLY', 'Weekly'
        MONTHLY = 'MONTHLY', 'Monthly'
    
    name = models.CharField(max_length=50, choices=PlanType.choices)
    duration_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['duration_days']
    
    def __str__(self):
        return f"{self.name} ({self.duration_days} days) - ${self.price}"


class WorkspaceTag(models.Model):
    """
    Unique workspace tags as per Section 6.3
    Tags are assigned to active bookings and prevent conflicts.
    """
    tag_code = models.CharField(max_length=20, unique=True)
    is_available = models.BooleanField(default=True)
    current_booking = models.ForeignKey(
        'Booking', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tag'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.tag_code


class Booking(models.Model):
    """
    Workspace booking model as per Section 6.2
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Payment'
        ACTIVE = 'ACTIVE', 'Active'
        EXPIRED = 'EXPIRED', 'Expired'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings',
        limit_choices_to={'role': User.Role.CUSTOMER}
    )
    workspace_plan = models.ForeignKey(
        WorkspacePlan, 
        on_delete=models.PROTECT,
        related_name='bookings'
    )
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    payment_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Customer details (stored at time of booking)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"Booking {self.id} - {self.customer_name} ({self.status})"
    
    def activate(self):
        """Activate booking and assign a tag"""
        from django.db import transaction
        
        with transaction.atomic():
            self.status = self.Status.ACTIVE
            self.payment_verified = True
            self.save()
            
            # Assign an available tag
            available_tag = WorkspaceTag.objects.filter(
                is_available=True
            ).select_for_update().first()
            
            if available_tag:
                available_tag.is_available = False
                available_tag.current_booking = self
                available_tag.save()
    
    def expire(self):
        """Expire booking and release tag"""
        from django.db import transaction
        
        with transaction.atomic():
            self.status = self.Status.EXPIRED
            self.save()
            
            # Release the tag back to pool
            if hasattr(self, 'assigned_tag'):
                tag = self.assigned_tag
                tag.is_available = True
                tag.current_booking = None
                tag.save()