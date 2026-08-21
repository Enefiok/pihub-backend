import uuid
from django.db import models
from accounts.models import User
from courses.models import Course

class Certificate(models.Model):
    """
    Certificate generation and verification as per Section 8.
    """
    # Generate a unique ID automatically
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='certificates')
    
    student_name = models.CharField(max_length=100, help_text="Name as it should appear on the certificate")
    issue_date = models.DateField(auto_now_add=True)
    
    is_verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificate {self.certificate_id} for {self.student_name}"