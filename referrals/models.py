import random
import string
from django.db import models, transaction
from django.utils import timezone
from accounts.models import User
from courses.models import Course, Student

class Influencer(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    social_handle = models.CharField(max_length=100, blank=True, help_text="e.g., @john_doe")
    default_commission_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00, help_text="Default commission percentage (0-100)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ReferralCode(models.Model):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE, related_name='referral_codes')
    code = models.CharField(max_length=50, unique=True, help_text="Stored uppercase, matched case-insensitively")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Discount percentage (0-100)")
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission percentage (0-100)")
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited uses")
    
    # FIX: Added related_name to prevent clash with other apps
    applicable_courses = models.ManyToManyField(
        Course, blank=True, related_name='applicable_referral_codes', help_text="Leave empty to apply to all courses"
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_referral_codes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.upper().strip()
        if not self.commission_percent:
            self.commission_percent = self.influencer.default_commission_percent
        super().save(*args, **kwargs)

    @classmethod
    def generate_code(cls, influencer_name, length=4):
        prefix = "".join(filter(str.isalpha, influencer_name.upper()))[:3] or "INF"
        random_digits = "".join(random.choices(string.digits, k=length))
        return f"{prefix}{random_digits}"

    def get_current_uses(self):
        return self.registrations.exclude(status='cancelled').count()

    def is_valid_for_course(self, course):
        if not self.is_active:
            return False, "This referral code is inactive."
        if self.expires_at and self.expires_at < timezone.now():
            return False, "This referral code has expired."
        if self.max_uses is not None and self.get_current_uses() >= self.max_uses:
            return False, "This referral code has reached its maximum usage limit."
        if self.applicable_courses.exists() and not self.applicable_courses.filter(id=course.id).exists():
            return False, "This referral code is not valid for this course."
        return True, "Valid"


class CourseRegistration(models.Model):
    class PaymentOption(models.TextChoices):
        PAY_NOW = 'pay_now', 'Pay Now'
        PAY_LATER = 'pay_later', 'Pay Later'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='registrations')
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    payment_option = models.CharField(max_length=20, choices=PaymentOption.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    referral_code = models.ForeignKey(ReferralCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent_applied = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # FIX: related_name changed to 'course_registration_record' to avoid clashing with Payment's field name
    payment = models.OneToOneField(
        'payments.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='course_registration_record'
    )
    
    student = models.ForeignKey('courses.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'course'],
                condition=models.Q(status='pending'),
                name='unique_pending_reg_per_email_course' # FIX: Shortened name to ensure uniqueness
            )
        ]

    def __str__(self):
        return f"{self.full_name} - {self.course.title} ({self.status})"

    def mark_as_paid(self, payment_instance=None):
        if self.status == self.Status.PENDING:
            self.status = self.Status.PAID
            self.paid_at = timezone.now()
            if payment_instance:
                self.payment = payment_instance
            self.save()
            
            if not self.student and self.email:
                self.student, _ = Student.objects.get_or_create(
                    email=self.email,
                    course=self.course,
                    defaults={'name': self.full_name, 'phone': self.phone, 'status': Student.Status.ACTIVE}
                )
                self.save()