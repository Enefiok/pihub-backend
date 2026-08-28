from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubscribeView, UnsubscribeView, NewsletterViewSet,
    PublicGalleryListView, PublicEnquiryCreateView,
    StaffGalleryViewSet, StaffEnquiryViewSet
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'newsletters', NewsletterViewSet, basename='newsletter')
router.register(r'staff/gallery', StaffGalleryViewSet, basename='staff-gallery')
router.register(r'staff/enquiries', StaffEnquiryViewSet, basename='staff-enquiry')

urlpatterns = [
    # Public endpoints
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/<uuid:token>/', UnsubscribeView.as_view(), name='unsubscribe'),
    path('gallery/', PublicGalleryListView.as_view(), name='public-gallery'),
    path('enquiries/', PublicEnquiryCreateView.as_view(), name='public-enquiry'),
    
    # Staff Dashboard endpoints (handled by the router)
    path('', include(router.urls)),
]