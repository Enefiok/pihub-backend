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
    Handles booking creation for guest customers (public), 
    and viewing for authenticated staff.
    """
    serializer_class = BookingSerializer

    def get_permissions(self):
        # Anyone can create a booking (guest checkout)
        if self.action == 'create':
            return [permissions.AllowAny()]
        # Only authenticated staff can view/list bookings
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Staff (Admin, Receptionist, CEO, Lead Dev) can see all bookings
        if user.is_authenticated and user.role in [
            user.Role.ADMIN, 
            user.Role.RECEPTIONIST, 
            user.Role.CEO, 
            user.Role.LEAD_DEVELOPER
        ]:
            return Booking.objects.all()
        return Booking.objects.none()

    def perform_create(self, serializer):
        serializer.save()