from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import WorkspacePlan, WorkspaceTag, Booking
from .serializers import WorkspacePlanSerializer, BookingSerializer

class WorkspacePlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Publicly accessible list of workspace plans.
    """
    queryset = WorkspacePlan.objects.filter(is_active=True)
    serializer_class = WorkspacePlanSerializer
    permission_classes = [permissions.AllowAny]


class BookingViewSet(viewsets.ModelViewSet):
    """
    Handles booking creation for customers, and viewing for staff.
    """
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        # Customers can only see their own bookings
        if user.role == user.Role.CUSTOMER:
            return Booking.objects.filter(customer=user)
        # Staff (Admin, Receptionist, CEO, Lead Dev) can see all bookings
        return Booking.objects.all()

    def get_permissions(self):
        # Only authenticated users can create or view bookings
        if self.action in ['create', 'list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        # The serializer's create() method handles setting the customer and dates
        serializer.save()