from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password.")
            
            # CRITICAL FIX: Ensure only Staff can log in
            if user.role == User.Role.CUSTOMER:
                raise serializers.ValidationError("Customer accounts cannot log into the dashboard.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        data['user'] = user
        return data


class StaffCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for Admins/CEOs to create new staff members.
    """
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone_number', 'is_active']

    def validate_role(self, value):
        # Prevent assigning the CUSTOMER role via this staff creation endpoint
        if value == User.Role.CUSTOMER:
            raise serializers.ValidationError("Cannot assign CUSTOMER role via staff dashboard.")
        return value

    def create(self, validated_data):
        # Create the user with the role chosen by the Admin/CEO
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.ADMIN), # Defaults to ADMIN if not specified
            phone_number=validated_data.get('phone_number', ''),
            is_staff=True, # Always make them staff so they can access the dashboard
            is_active=validated_data.get('is_active', True)
        )
        # Create a token for them immediately so they can log in
        Token.objects.create(user=user)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for a logged-in user to change their own password.
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = self.context['request'].user
        
        # 1. Check if the old password is correct
        if not user.check_password(data.get('old_password')):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})
        
        # 2. Check if new passwords match
        if data.get('new_password') != data.get('confirm_new_password'):
            raise serializers.ValidationError({"confirm_new_password": "New passwords do not match."})
            
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        # Set the new password and save the user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user