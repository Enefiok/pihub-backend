from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    # SHIELD FOR FRONTEND: Explicitly make these optional so missing keys don't cause 400 errors
    requirements = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'duration', 
            'requirements', 'image', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']