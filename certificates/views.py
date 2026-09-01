from rest_framework import generics, status, permissions
from rest_framework.response import Response
from accounts.permissions import IsManagementOrReadOnly
from .models import Certificate
from .serializers import CertificateSerializer

class CertificateListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for staff to list and create certificates.
    - GET: All staff can view (list) certificates.
    - POST: Only CEO/Lead Dev/Admin can issue a new certificate.
    """
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsManagementOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the issued_by field to the current logged-in staff
        serializer.save(issued_by=self.request.user)


class CertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for staff to view, update, or delete a specific certificate.
    - GET: All staff can view.
    - PUT/PATCH/DELETE: Only CEO/Lead Dev/Admin.
    """
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsManagementOrReadOnly]
    lookup_field = 'certificate_id'


class CertificateVerifyView(generics.RetrieveAPIView):
    """
    Public endpoint to verify a certificate by its unique UUID.
    Anyone can access this without authentication.
    """
    queryset = Certificate.objects.filter(is_verified=True)
    serializer_class = CertificateSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'certificate_id'

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({
                "is_valid": True,
                "message": "This is a valid PIHUB certificate.",
                "certificate": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Certificate.DoesNotExist:
            return Response({
                "is_valid": False,
                "message": "Certificate not found or has been revoked."
            }, status=status.HTTP_404_NOT_FOUND)