from rest_framework import serializers
from django.utils.text import slugify
from .models import BlogPost, BlogCategory

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 
            'content', 'featured_image', 'author', 'author_name', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'author', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        # Try to get full name, fallback to username
        if hasattr(obj.author, 'get_full_name'):
            full_name = obj.author.get_full_name()
            if full_name:
                return full_name
        return obj.author.username

    def create(self, validated_data):
        # Auto-generate slug from title if not provided
        if 'slug' not in validated_data or not validated_data['slug']:
            title = validated_data.get('title', '')
            validated_data['slug'] = slugify(title)
        
        # Automatically set the author to the logged-in staff member
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)   