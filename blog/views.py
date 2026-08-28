from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from .models import BlogPost, BlogCategory
from .serializers import BlogPostSerializer, BlogCategorySerializer

# --- PUBLIC ENDPOINTS (For the Website) ---

class PublicBlogPostListView(generics.ListAPIView):
    """Fetches only PUBLISHED blog posts for the public website."""
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BlogPost.objects.filter(status='PUBLISHED').order_by('-created_at')

class PublicBlogPostDetailView(generics.RetrieveAPIView):
    """Fetches a single published blog post by its ID or Slug."""
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug' # Allows fetching by URL like /api/blog/posts/my-first-post/

    def get_queryset(self):
        return BlogPost.objects.filter(status='PUBLISHED')


# --- STAFF ENDPOINTS (For Custom Admin Dashboard) ---

class StaffBlogCategoryViewSet(viewsets.ModelViewSet):
    """Full CRUD for Blog Categories. Staff only."""
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

class StaffBlogPostViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Blog Posts. Staff only.
    Allows filtering by status (e.g., ?status=DRAFT) in the dashboard.
    """
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Staff can see ALL posts (Drafts and Published)
        queryset = BlogPost.objects.all().order_by('-created_at')
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_update(self, serializer):
        # Ensure author doesn't change on update
        serializer.save(author=self.request.user)