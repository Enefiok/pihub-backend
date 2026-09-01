from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from accounts.models import User  # Imported to check user roles
from accounts.permissions import IsManagementOrReadOnly, IsManagementOrReceptionistCreateOnly
from .models import WorkspacePlan, WorkspaceTag, Booking
from .serializers import WorkspacePlanSerializer, BookingSerializer, WorkspaceTagSerializer


class WorkspacePlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for workspace plans.
    - Public: Can view active plans (Read-only)
    - Staff: All can view; only CEO/Lead Dev/Admin can create, update, delete.
    """
    serializer_class = WorkspacePlanSerializer

    def get_permissions(self):
        # Public can only view (GET requests)
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        # Staff writes are restricted to management roles
        return [IsManagementOrReadOnly()]

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
    viewing for authenticated staff, and walk-in bookings for
    customers who pay in person at the front desk.
    - Staff: All can view; CEO/Lead Dev/Admin can edit/delete;
      Receptionist can additionally create walk-ins.
    """
    serializer_class = BookingSerializer

    def get_permissions(self):
        # Anyone can create a booking (guest checkout)
        if self.action == 'create':
            return [permissions.AllowAny()]
        # Walk-in bookings: management + Receptionist only
        if self.action == 'walk_in':
            return [IsManagementOrReceptionistCreateOnly()]
        # List/retrieve/update/delete: management + Receptionist can view,
        # but only management can edit/delete (enforced by the permission class)
        return [IsManagementOrReceptionistCreateOnly()]

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

    @action(detail=False, methods=['post'])
    def walk_in(self, request):
        """
        Staff-only: create a booking for a customer who paid in person
        at the front desk, and immediately activate it — assigning an
        available tag right away so staff can hand it over on the spot.

        Only customer_name and workspace_plan are truly required. Email
        is auto-filled with a placeholder if the customer didn't give one
        (the model requires an email, but walk-in customers often won't
        give one, especially for quick daily visits).
        """
        data = request.data.copy()

        # Auto-generate a placeholder email if none provided
        if not data.get('customer_email'):
            data['customer_email'] = f"walkin+{int(timezone.now().timestamp())}@pihub.local"

        # Default start_date to right now if admin didn't set one
        if not data.get('start_date'):
            data['start_date'] = timezone.now().isoformat()

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()  # status defaults to PENDING inside serializer.create()

        tag_assigned = booking.activate()

        # Record this as a manual/in-person payment for the accounting trail
        try:
            from payments.models import Payment
            Payment.objects.create(
                booking=booking,
                amount=booking.workspace_plan.price,
                gateway=Payment.Gateway.MANUAL,
                status=Payment.Status.SUCCESS,
                transaction_id=f"MANUAL-{booking.id}-{int(timezone.now().timestamp())}",
            )
        except Exception:
            pass  # Don't block the booking if the Payment record fails for any reason

        booking.refresh_from_db()
        response_serializer = BookingSerializer(booking)

        return Response({
            "message": "Walk-in booking created and tag assigned." if tag_assigned else "Booking created, but no tags are currently available.",
            "booking": response_serializer.data,
            "tag_assigned": tag_assigned,
        }, status=status.HTTP_201_CREATED)


class WorkspaceTagViewSet(viewsets.ModelViewSet):
    """
    Staff-only endpoint to view and manage workspace tags.
    All staff can view; only CEO/Lead Dev/Admin can create, update, delete.
    """
    serializer_class = WorkspaceTagSerializer
    permission_classes = [IsManagementOrReadOnly]
    queryset = WorkspaceTag.objects.all()