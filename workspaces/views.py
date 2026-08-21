from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from accounts.models import User  # Imported to check user roles
from .models import WorkspacePlan, WorkspaceTag, Booking
from .serializers import WorkspacePlanSerializer, BookingSerializer


class WorkspacePlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workspace plans.
    - Public: Can view active plans (Read-only)
    - Staff: Can create, update, delete plans (Full CRUD)
    """
    serializer_class = WorkspacePlanSerializer

    def get_permissions(self):
        # Public can only view (GET requests)
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        # Staff must be authenticated to create/update/delete
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Public only sees active plans
        if user.is_anonymous or user.role == User.Role.CUSTOMER:
            return WorkspacePlan.objects.filter(is_active=True)
        # Staff sees all plans (including inactive ones they might want to reactivate)
        return WorkspacePlan.objects.all()

    def perform_create(self, serializer):
        # Double-check role just in case
        if not self.request.user.is_authenticated or self.request.user.role == User.Role.CUSTOMER:
            raise permissions.PermissionDenied("Only staff can create workspace plans.")
        serializer.save()


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