from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User model for PIHUB.
    Extends Django's default AbstractUser to add role-based access.
    """
    class Role(models.TextChoices):
        CEO = 'CEO', 'CEO'
        LEAD_DEVELOPER = 'LEAD_DEVELOPER', 'Lead Developer'
        ADMIN = 'ADMIN', 'Admin'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'
        CUSTOMER = 'CUSTOMER', 'Customer'

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.CUSTOMER,
        help_text="The user's role in the PIHUB system."
    )
    
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        help_text="Optional phone number for the user."
    )

    def __str__(self):
        return self.username or self.email