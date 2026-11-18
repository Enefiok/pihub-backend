from django.db import models
from django.utils.text import slugify
from accounts.models import User
from cloudinary.models import CloudinaryField

class Course(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        UNAVAILABLE = 'UNAVAILABLE', 'Unavailable'
        COMING_SOON = 'COMING_SOON', 'Coming Soon'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    duration = models.CharField(max_length=50, help_text="e.g., 4 weeks, 3 days")
    
    # NEW FIELD: Required for referral discount calculations
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Base price of the course in NGN.")
    
    requirements = models.TextField(blank=True, null=True, default='', help_text="Optional: Prerequisites or things needed.")
    image = CloudinaryField('image', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught', help_text="The instructor assigned to teach this course.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class Student(models.Model):
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