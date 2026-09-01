from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentViewSet

router = DefaultRouter()
# 'students' MUST be registered before the empty prefix, or CourseViewSet's
# detail route (r'') swallows /api/courses/students/ as if "students" were
# a Course ID, causing 404s and "Method not allowed" errors.
router.register(r'students', StudentViewSet, basename='student')
router.register(r'', CourseViewSet, basename='course')  # Changed 'courses' to '' so the URL doesn't repeat the word

urlpatterns = [
    path('', include(router.urls)),
]