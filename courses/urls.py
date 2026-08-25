from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

router = DefaultRouter()
# Changed 'courses' to '' so the URL doesn't repeat the word
router.register(r'', CourseViewSet, basename='course') 

urlpatterns = [
    path('', include(router.urls)),
]