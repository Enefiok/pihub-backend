from django.contrib.sitemaps import Sitemap
from .models import BlogPost

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Only list published blog posts
        return BlogPost.objects.filter(status='PUBLISHED')

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # Points to your frontend read page with the slug
        return f"/read.html?slug={obj.slug}"


class StaticSitemap(Sitemap):
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        # List your core static HTML pages
        return ['index', 'about', 'blog', 'offer', 'contactus']

    def location(self, item):
        if item == 'index':
            return "/"
        return f"/{item}.html"