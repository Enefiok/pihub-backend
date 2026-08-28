from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Subscriber, Newsletter, GalleryImage, Enquiry
from .serializers import SubscribeSerializer, NewsletterSerializer, GalleryImageSerializer, EnquirySerializer

# --- PUBLIC ENDPOINTS ---

class SubscribeView(generics.CreateAPIView):
    """Public endpoint for users to subscribe to the newsletter."""
    queryset = Subscriber.objects.all()
    serializer_class = SubscribeSerializer
    permission_classes = [permissions.AllowAny]

class UnsubscribeView(generics.GenericAPIView):
    """Public endpoint for users to unsubscribe using their secure token."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, token, *args, **kwargs):
        try:
            subscriber = Subscriber.objects.get(unsubscribe_token=token)
            subscriber.is_active = False
            subscriber.save()
            return Response({"message": "You have been successfully unsubscribed."}, status=status.HTTP_200_OK)
        except Subscriber.DoesNotExist:
            return Response({"error": "Invalid or expired unsubscribe link."}, status=status.HTTP_404_NOT_FOUND)

class PublicGalleryListView(generics.ListAPIView):
    """Fetches active gallery images for the frontend, ordered by display_order."""
    serializer_class = GalleryImageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = GalleryImage.objects.filter(is_active=True)
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

class PublicEnquiryCreateView(generics.CreateAPIView):
    """Allows public users to submit contact enquiries."""
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    permission_classes = [permissions.AllowAny]


# --- STAFF ENDPOINTS (For Custom Admin Dashboard) ---

class NewsletterViewSet(viewsets.ModelViewSet):
    """API endpoint for staff to manage newsletters (CRUD)."""
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        newsletter = self.get_object()
        if newsletter.is_sent:
            return Response({"error": "This newsletter has already been sent."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sent_count = newsletter.send()
            return Response({
                "message": f"Newsletter sent successfully to {sent_count} subscribers.",
                "sent_count": sent_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to send newsletter: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StaffGalleryViewSet(viewsets.ModelViewSet):
    """Full CRUD for Gallery Images. Staff only."""
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [permissions.IsAuthenticated]

class StaffEnquiryViewSet(viewsets.ModelViewSet):
    """Staff can view all enquiries and update their status (e.g., mark as RESOLVED)."""
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Enquiry.objects.all()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset