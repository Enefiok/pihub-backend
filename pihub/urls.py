"""
URL configuration for pihub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/accounts/', include('accounts.urls')),
    path('api/workspaces/', include('workspaces.urls')),
    path('api/core/', include('core.urls')), # <--- Added this line
]

# Serve media files (like course and blog images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)