from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentViewSet, CourseRegistrationView

router = DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')
router.register(r'', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', CourseRegistrationView.as_view(), name='course-register'),
]