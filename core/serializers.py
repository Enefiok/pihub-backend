import cloudinary
from rest_framework import serializers
from .models import Subscriber, Newsletter, GalleryImage, Enquiry
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['email']

    def create(self, validated_data):
        email = validated_data['email']
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        
        if created or not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save()
            
            try:
                context = {
                    'unsubscribe_link': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/unsubscribe/{subscriber.unsubscribe_token}/"
                }
                html_content = render_to_string('core/emails/welcome.html', context)
                text_content = strip_tags(html_content)
                
                msg = EmailMultiAlternatives(
                    subject="Welcome to the PIHUB Newsletter!",
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                logger.info(f"Welcome email sent successfully to {email}")
            except Exception as e:
                logger.error(f"Failed to send welcome email to {email}: {str(e)}")
            
        return subscriber

class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ['id', 'email', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['id', 'subject', 'content', 'is_sent', 'sent_at', 'created_at']
        read_only_fields = ['id', 'is_sent', 'sent_at', 'created_at']

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ['id', 'title', 'image', 'category', 'display_order', 'is_active', 'created_at']

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

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ['id', 'name', 'email', 'phone', 'service_type', 'subject', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']