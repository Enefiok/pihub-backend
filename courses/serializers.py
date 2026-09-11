from rest_framework import serializers
from .models import Course, Student

class CourseSerializer(serializers.ModelSerializer):
    # SHIELD FOR FRONTEND: Explicitly make these optional so missing keys don't cause 400 errors
    requirements = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # CHANGE: Use SerializerMethodField to return the full absolute URL
    image = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 
            'requirements', 'image', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    # ADD THIS METHOD:
    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
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