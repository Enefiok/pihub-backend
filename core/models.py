import uuid
from django.db import models
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField(help_text="Write your newsletter content here. You can use basic HTML.")
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.subject

    def send(self):
        """Sends the newsletter to all active subscribers."""
        active_subscribers = Subscriber.objects.filter(is_active=True)
        if not active_subscribers.exists():
            return 0

        connection = get_connection() # Opens a single connection for efficiency
        connection.open()
        
        messages = []
        for sub in active_subscribers:
            context = {
                'content': self.content,
                'unsubscribe_link': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/unsubscribe/{sub.unsubscribe_token}/"
            }
            
            html_content = render_to_string('core/emails/newsletter.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(
                subject=self.subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[sub.email],
                connection=connection
            )
            msg.attach_alternative(html_content, "text/html")
            messages.append(msg)
            
        connection.send_messages(messages)
        connection.close()
        
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()
        return len(messages)


class GalleryImage(models.Model):
    """Dynamic images for frontend carousels and galleries."""
    CATEGORY_CHOICES = [
        ('HOME_CAROUSEL', 'Home Carousel'),
        ('WORKSPACE', 'Workspace'),
        ('PODCAST', 'Podcast Studio'),
        ('EVENTS', 'Events'),
    ]
    
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='gallery/%Y/%m/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='HOME_CAROUSEL')
    display_order = models.PositiveIntegerField(default=0, help_text="Lower numbers display first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['display_order', '-created_at']
        
    def __str__(self):
        return self.title


class Enquiry(models.Model):
    """Contact enquiries for non-payment services."""
    SERVICE_CHOICES = [
        ('CONFERENCE_ROOM', 'Conference Room'),
        ('PRIVATE_SPACE', 'Private Space'),
        ('PODCAST', 'Podcast Studio'),
        ('GENERAL', 'General Enquiry'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Enquiry from {self.name} - {self.service_type}"