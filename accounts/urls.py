from django.urls import path
from .views import LoginView, StaffCreateView, ChangePasswordView

urlpatterns = [
    # Staff Login
    path('login/', LoginView.as_view(), name='auth-login'),
    
    # For Custom Admin Dashboard (CEO/Admin creates staff)
    path('create-staff/', StaffCreateView.as_view(), name='auth-create-staff'),
    
    # For Logged-in Staff to change their own password
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
]