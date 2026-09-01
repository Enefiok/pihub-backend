from django.urls import path
from .views import LoginView, StaffCreateView, StaffListView, AdminResetPasswordView, ChangePasswordView

urlpatterns = [
    # Staff Login
    path('login/', LoginView.as_view(), name='auth-login'),
    
    # For Custom Admin Dashboard (CEO/Admin creates staff)
    path('create-staff/', StaffCreateView.as_view(), name='auth-create-staff'),
    
    # For CEO/Lead Dev to view all existing staff accounts
    path('staff/', StaffListView.as_view(), name='auth-staff-list'),
    
    # For CEO/Lead Dev to forcibly reset another staff member's password
    path('staff/<int:user_id>/reset-password/', AdminResetPasswordView.as_view(), name='auth-admin-reset-password'),
    
    # For Logged-in Staff to change their own password
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
]