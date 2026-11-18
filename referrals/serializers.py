from rest_framework import serializers
from django.utils import timezone
from .models import Influencer, ReferralCode, CourseRegistration
from courses.models import Course

class InfluencerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Influencer
        fields = ['id', 'name', 'email', 'phone', 'social_handle', 'default_commission_percent', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReferralCodeSerializer(serializers.ModelSerializer):
    influencer_name = serializers.CharField(source='influencer.name', read_only=True)
    applicable_course_titles = serializers.SerializerMethodField()
    current_uses = serializers.SerializerMethodField()
    total_conversions = serializers.SerializerMethodField()

    class Meta:
        model = ReferralCode
        fields = [
            'id', 'influencer', 'influencer_name', 'code', 'discount_percent', 
            'commission_percent', 'is_active', 'expires_at', 'max_uses', 
            'current_uses', 'total_conversions', 'applicable_courses', 'applicable_course_titles', 'created_at'
        ]
        read_only_fields = ['id', 'current_uses', 'total_conversions', 'created_at']

    def get_applicable_course_titles(self, obj):
        return list(obj.applicable_courses.values_list('title', flat=True))

    def get_current_uses(self, obj):
        return obj.get_current_uses()

    def get_total_conversions(self, obj):
        return obj.registrations.filter(status='paid').count()

    def create(self, validated_data):
        applicable_courses = validated_data.pop('applicable_courses', [])
        code = ReferralCode.objects.create(**validated_data)
        if applicable_courses:
            code.applicable_courses.set(applicable_courses)
        return code


class ReferralValidationSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    course_id = serializers.IntegerField(required=True)

    def validate(self, data):
        code = data['code'].strip().upper()
        course_id = data['course_id']
        
        try:
            course = Course.objects.get(id=course_id, status=Course.Status.ACTIVE)
        except Course.DoesNotExist:
            raise serializers.ValidationError({"course_id": "Course not found or inactive."})

        try:
            referral_code = ReferralCode.objects.select_related('influencer').get(code=code)
        except ReferralCode.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid referral code."})

        is_valid, message = referral_code.is_valid_for_course(course)
        if not is_valid:
            raise serializers.ValidationError({"code": message})

        discount_amount = (course.price * referral_code.discount_percent) / 100
        final_price = course.price - discount_amount

        data['course'] = course
        data['referral_code'] = referral_code
        data['original_price'] = course.price
        data['discount_amount'] = discount_amount
        data['final_price'] = final_price
        return data


class RegistrationAnalyticsSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    influencer_name = serializers.CharField(source='referral_code.influencer.name', read_only=True, default='None')
    code_used = serializers.CharField(source='referral_code.code', read_only=True, default='None')

    class Meta:
        model = CourseRegistration
        fields = [
            'id', 'full_name', 'email', 'course', 'course_title', 'status', 'payment_option',
            'original_price', 'discount_amount', 'final_price', 'commission_amount',
            'influencer_name', 'code_used', 'created_at', 'paid_at'
        ]
        read_only_fields = fields