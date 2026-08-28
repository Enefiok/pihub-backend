from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PublicBlogPostListView, PublicBlogPostDetailView,
    StaffBlogPostViewSet, StaffBlogCategoryViewSet
)

router = DefaultRouter()
router.register(r'staff/categories', StaffBlogCategoryViewSet, basename='staff-blog-category')
router.register(r'staff/posts', StaffBlogPostViewSet, basename='staff-blog-post')

urlpatterns = [
    # Public Endpoints
    path('posts/', PublicBlogPostListView.as_view(), name='public-blog-list'),
    path('posts/<slug:slug>/', PublicBlogPostDetailView.as_view(), name='public-blog-detail'),
    
    # Staff Dashboard Endpoints (Handled by Router)
    path('', include(router.urls)),
]