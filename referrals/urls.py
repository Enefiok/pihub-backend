from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReferralValidateView, InfluencerViewSet, ReferralCodeViewSet, 
    CourseRegistrationAdminViewSet, ReferralAnalyticsView
)

router = DefaultRouter()
router.register(r'influencers', InfluencerViewSet, basename='influencer')
router.register(r'codes', ReferralCodeViewSet, basename='referral-code')
router.register(r'registrations', CourseRegistrationAdminViewSet, basename='registration')

urlpatterns = [
    path('validate/', ReferralValidateView.as_view(), name='referral-validate'),
    path('analytics/', ReferralAnalyticsView.as_view(), name='referral-analytics'),
    path('', include(router.urls)),
]