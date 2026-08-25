from django.db import models
from django.utils.text import slugify
from accounts.models import User

class Course(models.Model):
    """
    PIHUB Courses as per Section 7
    """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        UNAVAILABLE = 'UNAVAILABLE', 'Unavailable'
        COMING_SOON = 'COMING_SOON', 'Coming Soon'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    duration = models.CharField(max_length=50, help_text="e.g., 4 weeks, 3 days")
    
    # UPDATED: Made strictly optional for the database and frontend
    requirements = models.TextField(
        blank=True, 
        null=True, 
        default='', 
        help_text="Optional: Prerequisites or things needed for the course."
    )
    
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Enrollment(models.Model):
    """
    Tracks students enrolled in courses.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"