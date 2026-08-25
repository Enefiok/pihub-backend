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
    
    # REMOVED: student ForeignKey because students don't have user accounts!
    
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='certificates')
    
    student_name = models.CharField(max_length=100, help_text="Name as it should appear on the certificate")
    student_email = models.EmailField(blank=True, null=True, help_text="Optional: Student's email for records")
    
    # Tracks which Admin/CEO issued this certificate
    issued_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='issued_certificates',
        help_text="The staff member who issued this certificate"
    )
    
    issue_date = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificate {self.certificate_id} for {self.student_name}"