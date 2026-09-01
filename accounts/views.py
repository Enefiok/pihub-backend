from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from accounts.permissions import IsManagementStrict
from .serializers import (
    LoginSerializer, StaffCreateSerializer, StaffListSerializer,
    ChangePasswordSerializer, AdminResetPasswordSerializer,
)
from .models import User

class StaffCreateView(generics.CreateAPIView):
    """
    API endpoint for the Custom Admin Dashboard.
    Only authenticated CEOs, Lead Developers, or Superusers can create new staff and assign roles.
    """
    serializer_class = StaffCreateSerializer
    permission_classes = [IsManagementStrict]

    def create(self, request, *args, **kwargs):
        # SECURITY CHECK: Only high-level roles can create new staff
        allowed_roles = [User.Role.CEO, User.Role.LEAD_DEVELOPER]
        if request.user.role not in allowed_roles and not request.user.is_superuser:
            return Response(
                {"error": "Only the CEO, Lead Developer, or Super Admin can create new staff members."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            "message": "Staff member created successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            }
        }, status=status.HTTP_201_CREATED)


class StaffListView(generics.ListAPIView):
    """
    API endpoint for CEO/Lead Dev to view all existing staff accounts.
    Excludes CUSTOMER-role accounts, since those aren't managed here.
    """
    serializer_class = StaffListSerializer
    permission_classes = [IsManagementStrict]

    def get_queryset(self):
        # Only CEO/Lead Dev (or superuser) can view the staff list
        allowed_roles = [User.Role.CEO, User.Role.LEAD_DEVELOPER]
        if self.request.user.role not in allowed_roles and not self.request.user.is_superuser:
            return User.objects.none()
        return User.objects.exclude(role=User.Role.CUSTOMER).order_by('-date_joined')


class AdminResetPasswordView(APIView):
    """
    API endpoint for CEO/Lead Dev to forcibly reset another staff member's
    password (e.g. they forgot it). Requires the requesting admin's own
    password as confirmation before the reset is applied.
    """
    permission_classes = [IsManagementStrict]

    def patch(self, request, user_id, *args, **kwargs):
        allowed_roles = [User.Role.CEO, User.Role.LEAD_DEVELOPER]
        if request.user.role not in allowed_roles and not request.user.is_superuser:
            return Response(
                {"error": "Only the CEO, Lead Developer, or Super Admin can reset staff passwords."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Staff member not found."}, status=status.HTTP_404_NOT_FOUND)

        if target_user.role == User.Role.CUSTOMER:
            return Response({"error": "Cannot reset passwords for customer accounts here."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AdminResetPasswordSerializer(
            data=request.data,
            context={'request': request, 'target_user': target_user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": f"Password reset successfully for {target_user.username}."
        }, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    """
    API endpoint for staff login. Returns the user data and auth token.
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            },
            "token": token.key
        }, status=status.HTTP_200_OK)


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for authenticated users to change their own password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Return the currently logged-in user
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Password updated successfully."
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)