"""
Views for user management.
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
import logging

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserLoginSerializer
)

logger = logging.getLogger('api')


class UserRegistrationView(APIView):
    """API endpoint for user registration."""
    
    def post(self, request):
        """Register a new user."""
        logger.info(f"User registration attempt: {request.data.get('email', 'N/A')}")
        
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
                    logger.info(f"User registered successfully: {user.email}")
                    
                    return Response({
                        'status': 'success',
                        'message': 'User registered successfully',
                        'data': UserSerializer(user).data
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error during user registration: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': 'An error occurred during registration'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.warning(f"User registration validation failed: {serializer.errors}")
        return Response({
            'status': 'error',
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """API endpoint for user login."""
    
    def post(self, request):
        """Authenticate and login a user."""
        logger.info(f"Login attempt: {request.data.get('email', 'N/A')}")
        
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                user.update_last_seen()
                logger.info(f"User logged in successfully: {user.email}")
                
                return Response({
                    'status': 'success',
                    'message': 'Login successful',
                    'data': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"Failed login attempt: {email}")
                return Response({
                    'status': 'error',
                    'message': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'status': 'error',
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """API endpoint for user logout."""
    
    def post(self, request):
        """Logout the current user."""
        if request.user.is_authenticated:
            logger.info(f"User logged out: {request.user.email}")
            logout(request)
            return Response({
                'status': 'success',
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'error',
            'message': 'No user is currently logged in'
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """API endpoint for user profile."""
    
    def get(self, request):
        """Get current user's profile."""
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        logger.info(f"Profile accessed: {request.user.email}")
        return Response({
            'status': 'success',
            'data': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """API endpoint to list all users."""
    
    serializer_class = UserSerializer
    
    def get_queryset(self):
        """Return all users except the current user."""
        if self.request.user.is_authenticated:
            return User.objects.exclude(id=self.request.user.id).order_by('-date_joined')
        return User.objects.none()
    
    def list(self, request, *args, **kwargs):
        """Return formatted response."""
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK) 