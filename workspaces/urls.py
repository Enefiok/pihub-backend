from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspacePlanViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'plans', WorkspacePlanViewSet, basename='workspace-plan')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]