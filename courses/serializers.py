import cloudinary
from rest_framework import serializers
from .models import Course, Student
from referrals.models import CourseRegistration, ReferralCode

class CourseSerializer(serializers.ModelSerializer):
    requirements = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 
            'price', 'requirements', 'image', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('image'):
            url = str(representation['image'])
            if not url.startswith('http'):
                cloud_name = cloudinary.config().cloud_name or 'grpuqogx'
                representation['image'] = f"https://res.cloudinary.com/{cloud_name}/{url}"
        return representation


class StudentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True, default=None)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'email', 'phone', 'course', 'course_title',
            'status', 'enrolled_date', 'notes'
        ]
        read_only_fields = ['id', 'enrolled_date']


class CourseRegistrationSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(status=Course.Status.ACTIVE),
        source='course',
        write_only=True
    )
    referral_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = CourseRegistration
        fields = [
            'course_id', 'full_name', 'email', 'phone', 
            'payment_option', 'referral_code'
        ]

    def validate_email(self, value):
        return value.lower().strip()