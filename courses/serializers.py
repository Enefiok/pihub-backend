import cloudinary
from rest_framework import serializers
from .models import Course, Student

class CourseSerializer(serializers.ModelSerializer):
    requirements = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 
            'requirements', 'image', 'status', 'created_at', 'updated_at'
        ]
        # 'image' is NOT read-only here, so uploads WILL work!
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def to_representation(self, instance):
        # 1. Get the default data (this allows the file upload to succeed)
        representation = super().to_representation(instance)
        
        # 2. Fix the image URL if Cloudinary returned a relative path
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