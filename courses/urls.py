from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentViewSet, CourseRegistrationView, PaymentStatusView

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'', CourseViewSet, basename='course')

urlpatterns = [
    # 1. Explicit paths MUST come before the router include
    path('register/', CourseRegistrationView.as_view(), name='course-register'),
    path('payment-status/', PaymentStatusView.as_view(), name='payment-status'),
    
    # 2. Router include comes last
    path('', include(router.urls)),
]