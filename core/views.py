from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Subscriber
from .serializers import SubscriberSerializer

class SubscribeView(generics.CreateAPIView):
    """
    API endpoint for frontend newsletter subscription.
    """
    serializer_class = SubscriberSerializer
    permission_classes = [permissions.AllowAny] # Anyone can subscribe

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {"message": "Successfully subscribed to the PIHUB newsletter!"}, 
            status=status.HTTP_201_CREATED
        )