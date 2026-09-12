import cloudinary
from rest_framework import serializers
from .models import Course, Student

class CourseSerializer(serializers.ModelSerializer):
    requirements = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 
            'requirements', 'image', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_image(self, obj):
        if obj.image:
            # CloudinaryField returns a CloudinaryResource, get the URL
            return obj.image.url
        return None

class StudentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True, default=None)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'email', 'phone', 'course', 'course_title',
            'status', 'enrolled_date', 'notes'
        ]
        read_only_fields = ['id', 'enrolled_date']