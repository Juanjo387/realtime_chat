"""
Tests for users app.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User


@pytest.mark.django_db
class TestUserRegistration:
    """Test user registration."""
    
    def test_successful_registration(self):
        """Test successful user registration."""
        client = APIClient()
        url = reverse('users:register')
        
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'SecurePassword123',
            'password_confirm': 'SecurePassword123'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'success'
        assert 'data' in response.data
        assert response.data['data']['email'] == 'test@example.com'
        
        # Verify user was created in database
        assert User.objects.filter(email='test@example.com').exists()
    
    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        client = APIClient()
        url = reverse('users:register')
        
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'SecurePassword123',
            'password_confirm': 'DifferentPassword123'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['status'] == 'error'
    
    def test_registration_invalid_email(self):
        """Test registration with invalid email."""
        client = APIClient()
        url = reverse('users:register')
        
        data = {
            'email': 'invalid-email',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'SecurePassword123',
            'password_confirm': 'SecurePassword123'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create a user first
        User.objects.create_user(
            email='test@example.com',
            first_name='Jane',
            last_name='Smith',
            password='Password123'
        )
        
        client = APIClient()
        url = reverse('users:register')
        
        data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'SecurePassword123',
            'password_confirm': 'SecurePassword123'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Test user login."""
    
    def test_successful_login(self):
        """Test successful user login."""
        # Create a user
        user = User.objects.create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='SecurePassword123'
        )
        
        client = APIClient()
        url = reverse('users:login')
        
        data = {
            'email': 'test@example.com',
            'password': 'SecurePassword123'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert response.data['data']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # Create a user
        User.objects.create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='SecurePassword123'
        )
        
        client = APIClient()
        url = reverse('users:login')
        
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Test user profile retrieval."""
    
    def test_get_profile_authenticated(self):
        """Test getting profile when authenticated."""
        user = User.objects.create_user(
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            password='SecurePassword123'
        )
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        url = reverse('users:profile')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert response.data['data']['email'] == 'test@example.com'
    
    def test_get_profile_unauthenticated(self):
        """Test getting profile when not authenticated."""
        client = APIClient()
        url = reverse('users:profile')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 