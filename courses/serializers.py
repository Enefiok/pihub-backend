from rest_framework import serializers
from .models import Course, Student

class CourseSerializer(serializers.ModelSerializer):
    # Make requirements optional
    requirements = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 
            'requirements', 'image', 'status', 'created_at', 'updated_at'
        ]
        # 'image' is NOT in read_only_fields, so DRF will accept the upload!
        # django-cloudinary-storage will automatically return the full URL.
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class StudentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True, default=None)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'email', 'phone', 'course', 'course_title',
            'status', 'enrolled_date', 'notes'
        ]
        read_only_fields = ['id', 'enrolled_date']