from django.db import models

class GalleryImage(models.Model):
    """
    Dynamic images for frontend carousels, sliders, and galleries.
    Managed entirely from the admin dashboard.
    """
    class Section(models.TextChoices):
        HOME_HERO = 'HOME_HERO', 'Home Hero Slider'
        ABOUT_US = 'ABOUT_US', 'About Us Gallery'
        GENERAL = 'GENERAL', 'General Gallery'

    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='gallery/')
    section = models.CharField(max_length=20, choices=Section.choices, default=Section.GENERAL)
    caption = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['section', 'display_order', '-created_at']

    def __str__(self):
        return self.title or f"Image {self.id}"


class Enquiry(models.Model):
    """
    Contact enquiries for services without direct online payment 
    (Conference Room, Private Spaces, Podcast).
    """
    class ServiceInterest(models.TextChoices):
        CONFERENCE_ROOM = 'CONFERENCE_ROOM', 'Conference Room'
        PRIVATE_SPACES = 'PRIVATE_SPACES', 'Private Spaces'
        PODCAST = 'PODCAST', 'Podcast'
        GENERAL = 'GENERAL', 'General Enquiry'

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    service_interest = models.CharField(max_length=20, choices=ServiceInterest.choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Enquiry from {self.name} - {self.service_interest}"