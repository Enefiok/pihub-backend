from django.urls import path
from .views import CertificateVerifyView, CertificateListCreateView, CertificateDetailView

urlpatterns = [
    # Staff management endpoints (auth required) - MUST be first or specific
    path('', CertificateListCreateView.as_view(), name='certificate-list-create'),
    path('<uuid:certificate_id>/', CertificateDetailView.as_view(), name='certificate-detail'),
    
    # Public verification endpoint (no auth required)
    path('verify/<uuid:certificate_id>/', CertificateVerifyView.as_view(), name='certificate-verify'),
]