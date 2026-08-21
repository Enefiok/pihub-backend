from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.CUSTOMER)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone_number']

    def create(self, validated_data):
        # Use create_user to ensure the password is hashed correctly
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', User.Role.CUSTOMER),
            phone_number=validated_data.get('phone_number', '')
        )
        # Generate an auth token for the new user
        Token.objects.create(user=user)
        return user


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
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        data['user'] = user
        return data