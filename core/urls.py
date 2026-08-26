from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubscribeView, UnsubscribeView, NewsletterViewSet

# Create a router and register our viewset
router = DefaultRouter()
router.register(r'newsletters', NewsletterViewSet, basename='newsletter')

urlpatterns = [
    # Public endpoints
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/<uuid:token>/', UnsubscribeView.as_view(), name='unsubscribe'),
    
    # Staff Newsletter Management endpoints (handled by the router)
    # This creates: /api/core/newsletters/ (GET, POST)
    # and: /api/core/newsletters/{id}/ (GET, PUT, PATCH, DELETE)
    # and: /api/core/newsletters/{id}/send/ (POST)
    path('', include(router.urls)),
]