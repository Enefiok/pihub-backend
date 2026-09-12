import cloudinary
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
    
    # We MUST use this to force the absolute URL, exactly like the working Gallery
    featured_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 
            'content', 'featured_image', 'author', 'author_name', 
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'author', 'created_at', 'updated_at']

    def get_author_name(self, obj):
        if hasattr(obj.author, 'get_full_name'):
            full_name = obj.author.get_full_name()
            if full_name:
                return full_name
        return obj.author.username

    def get_featured_image(self, obj):
        if obj.featured_image:
            url = str(obj.featured_image)
            # If it's already a full URL, return it
            if url.startswith('http'):
                return url
            # If it's a relative path, make it absolute
            cloud_name = cloudinary.config().cloud_name or 'grpuqogx'
            return f"https://res.cloudinary.com/{cloud_name}/{url}"
        return None

    def create(self, validated_data):
        if 'slug' not in validated_data or not validated_data['slug']:
            title = validated_data.get('title', '')
            validated_data['slug'] = slugify(title)
        
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)