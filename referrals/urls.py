from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReferralValidateView, InfluencerViewSet, ReferralCodeViewSet, 
    CourseRegistrationAdminViewSet, ReferralAnalyticsView,
    RegistrationActionView, RegistrationStatusUpdateView
)

router = DefaultRouter()
router.register(r'influencers', InfluencerViewSet, basename='influencer')
router.register(r'codes', ReferralCodeViewSet, basename='referral-code')
router.register(r'registrations', CourseRegistrationAdminViewSet, basename='registration')

urlpatterns = [
    path('validate/', ReferralValidateView.as_view(), name='referral-validate'),
    path('analytics/', ReferralAnalyticsView.as_view(), name='referral-analytics'),
    
    # Newly wired endpoints for single and bulk status updates
    path('registrations/action/', RegistrationActionView.as_view(), name='registration-action'),
    path('registrations/<int:pk>/status/', RegistrationStatusUpdateView.as_view(), name='registration-status'),
    
    path('', include(router.urls)),
]