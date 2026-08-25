from rest_framework import serializers
from .models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    # Read-only fields for a cleaner JSON response
    course_title = serializers.CharField(source='course.title', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Certificate
        fields = [
            'certificate_id', 
            'course',          # Writable: Accepts the Course ID (e.g., 1) from Postman
            'course_title',    # Read-only: Returns the course name in the response
            'student_name', 
            'student_email',
            'issued_by',       # Read-only: Auto-filled by the backend view
            'issued_by_name',  # Read-only: Returns the staff name in the response
            'issue_date', 
            'is_verified'
        ]
        # These fields cannot be changed via POST/PUT
        read_only_fields = ['certificate_id', 'issued_by', 'issue_date', 'course_title', 'issued_by_name']