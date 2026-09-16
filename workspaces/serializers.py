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
    tag_code = serializers.CharField(source='assigned_tag.tag_code', read_only=True, default=None)
    
    # 🔒 SECURITY: Make reference read-only so frontend can't spoof it, 
    # but it will still be included in the JSON response after creation!
    reference = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'workspace_plan', 'plan_name', 'plan_price',
            'status', 'start_date', 'end_date', 'payment_verified',
            'customer_name', 'customer_email', 'customer_phone', 
            'reference', 'tag_code', 'created_at'
        ]
        # Added 'reference' to read_only_fields for security
        read_only_fields = ['id', 'status', 'payment_verified', 'created_at', 'end_date', 'reference']

    def validate_start_date(self, value):
        """Ensure start date is not in the past. 
        We only check the DATE, so users can still book for 'today' 
        even if the hardcoded 10:00 AM time has already passed."""
        today = timezone.now().date()
        if value.date() < today:
            raise serializers.ValidationError("Start date cannot be in the past.")
        return value

    def create(self, validated_data):
        """
        Automatically calculate end_date based on the plan's duration.
        The model's save() method will automatically generate the 'reference'.
        """
        # .pop() removes the item from validated_data so it isn't passed twice to .create()
        plan = validated_data.pop('workspace_plan')
        start_date = validated_data.pop('start_date')
        
        # Calculate end date based on plan duration
        end_date = start_date + timedelta(days=plan.duration_days)
        
        # Create the booking in PENDING status
        # The model's save() method will auto-generate the reference here!
        booking = Booking.objects.create(
            workspace_plan=plan,
            status=Booking.Status.PENDING,
            start_date=start_date,
            end_date=end_date,
            **validated_data  
        )
        return booking


class WorkspaceTagSerializer(serializers.ModelSerializer):
    """
    Serializer for staff to view and manage workspace tags.
    Includes the customer name of whoever currently holds the tag, if any.
    """
    booking_customer_name = serializers.CharField(
        source='current_booking.customer_name', read_only=True, default=None
    )

    class Meta:
        model = WorkspaceTag
        fields = ['id', 'tag_code', 'is_available', 'current_booking', 'booking_customer_name', 'created_at']
        read_only_fields = ['id', 'current_booking', 'created_at']