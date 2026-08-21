from rest_framework import viewsets, permissions
from accounts.models import User
from .models import Course
from .serializers import CourseSerializer

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses.
    - Public: Can view active and coming-soon courses.
    - Staff: Can create, update, delete, and view all courses (including unavailable).
    """
    serializer_class = CourseSerializer

    def get_permissions(self):
        # Public can only view (GET requests)
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        # Staff must be authenticated to create/update/delete
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        
        # Public (anonymous or customer) only sees active and coming-soon courses
        if user.is_anonymous or (user.is_authenticated and user.role == User.Role.CUSTOMER):
            return Course.objects.filter(
                status__in=[Course.Status.ACTIVE, Course.Status.COMING_SOON]
            )
            
        # Staff sees all courses (including 'UNAVAILABLE' ones they might want to edit/reactivate)
        return Course.objects.all()

    def perform_create(self, serializer):
        # Double-check role just in case
        if not self.request.user.is_authenticated or self.request.user.role == User.Role.CUSTOMER:
            raise permissions.PermissionDenied("Only staff can create courses.")
        serializer.save()