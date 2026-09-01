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
    Legacy model — tracks enrollment for real User accounts.
    Not used by the admin dashboard since students don't have accounts
    in practice. Kept for potential future use; see Student model below
    for the model actually used to track who's studying at PIHUB.
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class Student(models.Model):
    """
    Tracks people actively studying at PIHUB, independent of Certificate
    (which only proves completion) and independent of User (students don't
    have login accounts). Admin adds a student here the moment someone
    starts a course, so PIHUB has a real count of who's currently enrolled,
    not just who's finished.
    """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        COMPLETED = 'COMPLETED', 'Completed'
        DROPPED = 'DROPPED', 'Dropped Out'

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    enrolled_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-enrolled_date']

    def __str__(self):
        return f"{self.name} - {self.course.title if self.course else 'No course'}"