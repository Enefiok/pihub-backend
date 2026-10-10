from django.db import models
from accounts.models import User
from cloudinary.models import CloudinaryField

class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """
    Blog management system as per Section 9.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PUBLISHED = 'PUBLISHED', 'Published'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    featured_image = CloudinaryField('image', blank=True, null=True)
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ NEW: Custom SEO Fields
    meta_title = models.CharField(max_length=70, blank=True, null=True)
    meta_description = models.TextField(max_length=160, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title  

    # ✅ NEW: Auto-generate meta_title if left blank
    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = f"{self.title} | PIHUB Akwa Ibom"
        super().save(*args, **kwargs)