"""
Serializers for user models.
"""
from rest_framework import serializers
from django.core.validators import EmailValidator
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text='Password must be at least 8 characters long'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
        extra_kwargs = {
            'first_name': {'required': True, 'min_length': 2},
            'last_name': {'required': True, 'min_length': 2},
        }
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        validator = EmailValidator()
        validator(value)
        
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        
        return value.lower()
    
    def validate_first_name(self, value):
        """Validate first name."""
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError('First name should contain only letters.')
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name."""
        if not value.replace(' ', '').isalpha():
            raise serializers.ValidationError('Last name should contain only letters.')
        return value.strip()
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'last_seen', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'last_seen']
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return obj.get_full_name()


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    ) 