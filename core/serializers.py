from rest_framework import serializers
from .models import Subscriber, Newsletter
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

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
            
            # Send welcome email
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
            
        return subscriber


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for staff to create and manage newsletters."""
    class Meta:
        model = Newsletter
        fields = ['id', 'subject', 'content', 'is_sent', 'sent_at', 'created_at']
        # These fields are read-only because they are handled automatically by the backend
        read_only_fields = ['id', 'is_sent', 'sent_at', 'created_at']