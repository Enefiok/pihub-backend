from rest_framework import viewsets, permissions
from accounts.models import User
from accounts.permissions import IsCourseInstructorOrManagement, IsManagementOrReadOnly
from .models import Course, Student
from .serializers import CourseSerializer, StudentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for courses.
    - Public: Can view ALL courses (frontend handles status display).
    - Staff: Can view all courses.
    - Management (CEO, Lead Dev, Admin): Full access (create/edit/delete any course).
    - Assigned Instructors: Can create, edit, update, and delete ONLY their own assigned courses.
    """
    serializer_class = CourseSerializer

    def get_permissions(self):
        # Public can only view (GET requests)
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
            
        # Restrict write actions to Management or the assigned Instructor
        return [IsCourseInstructorOrManagement()]

    def get_queryset(self):
        # EVERYONE sees all courses - frontend handles unavailable/coming soon display
        return Course.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or user.role == User.Role.CUSTOMER:
            raise permissions.PermissionDenied("Only staff can create courses.")

        # If an instructor creates a course, automatically assign them as the instructor
        if user.role == User.Role.INSTRUCTOR and 'instructor' not in serializer.validated_data:
            serializer.save(instructor=user)
        else:
            serializer.save()


class StudentViewSet(viewsets.ModelViewSet):
    """
    Staff-only endpoint to track students actively studying at PIHUB.
    Independent of Certificate (completion) and User (no login accounts).
    All staff can view; only CEO/Lead Dev/Admin can create, update, delete.
    """
    serializer_class = StudentSerializer
    permission_classes = [IsManagementOrReadOnly]
    queryset = Student.objects.all()