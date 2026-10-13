"""
URL configuration for pihub project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse  # ✅ NEW: For serving robots.txt

# ✅ NEW: Import sitemap view and the sitemap classes we created
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import BlogPostSitemap, StaticSitemap

# ✅ NEW: Register the sitemaps dictionary
sitemaps = {
    'blog': BlogPostSitemap,
    'static': StaticSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/accounts/', include('accounts.urls')),
    path('api/workspaces/', include('workspaces.urls')),
    path('api/certificates/', include('certificates.urls')),
    path('api/core/', include('core.urls')), 
    path('api/courses/', include('courses.urls')), 
    path('api/payments/', include('payments.urls')),
    path('api/blog/', include('blog.urls')),

    # ✅ NEW: Dynamic XML Sitemap endpoint
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # ✅ NEW: robots.txt endpoint (serves the text directly)
    path('robots.txt', lambda r: HttpResponse("User-agent: *\nAllow: /\n\nSitemap: https://pihubng.com/sitemap.xml", content_type="text/plain")),
]

# Serve media files (like course and blog images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)