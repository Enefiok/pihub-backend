from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source='booking.id', read_only=True, allow_null=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'transaction_id', 'amount', 'currency', 'gateway', 'status', 'booking_id', 'created_at']