from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import WorkspacePlan, WorkspaceTag, Booking

class WorkspacePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspacePlan
        fields = ['id', 'name', 'duration_days', 'price', 'description', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing bookings.
    Handles the creation of a PENDING booking for guest customers.
    """
    plan_name = serializers.CharField(source='workspace_plan.name', read_only=True)
    plan_price = serializers.DecimalField(source='workspace_plan.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'workspace_plan', 'plan_name', 'plan_price',
            'status', 'start_date', 'end_date', 'payment_verified',
            'customer_name', 'customer_email', 'customer_phone', 
            'reference', 'created_at'  # <-- ADDED 'reference' HERE
        ]
        # Notice 'reference' is NOT in read_only_fields. 
        # This allows the frontend (or Postman) to send it during checkout.
        read_only_fields = ['id', 'status', 'payment_verified', 'created_at', 'end_date']

    def validate_start_date(self, value):
        """Ensure start date is not in the past."""
        if value < timezone.now():
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value

    def create(self, validated_data):
        """
        Automatically calculate end_date based on the plan's duration.
        """
        # .pop() removes the item from validated_data so it isn't passed twice to .create()
        plan = validated_data.pop('workspace_plan')
        start_date = validated_data.pop('start_date')
        
        # Calculate end date based on plan duration
        end_date = start_date + timedelta(days=plan.duration_days)
        
        # Create the booking in PENDING status
        # Because we added 'reference' to the fields list, it will automatically 
        # be saved here if the frontend/Postman included it in the request!
        booking = Booking.objects.create(
            workspace_plan=plan,
            status=Booking.Status.PENDING,
            start_date=start_date,
            end_date=end_date,
            **validated_data  
        )
        return booking