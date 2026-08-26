from rest_framework import generics, status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Subscriber, Newsletter
from .serializers import SubscribeSerializer, NewsletterSerializer

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


class NewsletterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for staff to manage newsletters (CRUD).
    """
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.IsAuthenticated] # Only logged-in staff can access

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """
        Custom action to send a specific newsletter to all active subscribers.
        URL: POST /api/core/newsletters/{id}/send/
        """
        newsletter = self.get_object()
        
        if newsletter.is_sent:
            return Response(
                {"error": "This newsletter has already been sent."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Call the send() method we built in the model
            sent_count = newsletter.send()
            
            return Response({
                "message": f"Newsletter sent successfully to {sent_count} subscribers.",
                "sent_count": sent_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to send newsletter: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )