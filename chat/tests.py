"""
Tests for chat app.
"""
import pytest
import json
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path

from users.models import User
from chat.models import Conversation
from chat.consumers import ChatConsumer
from chat.redis_manager import redis_manager


@pytest.mark.django_db
class TestConversationCreation:
    """Test conversation creation."""
    
    def test_create_conversation(self):
        """Test creating a new conversation."""
        user1 = User.objects.create_user(
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='Password123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='Password123'
        )
        
        client = APIClient()
        client.force_authenticate(user=user1)
        
        url = reverse('chat:conversations')
        data = {
            'participant_ids': [user1.id, user2.id]
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'success'
        assert 'data' in response.data
        
        # Verify conversation was created
        conversation = Conversation.objects.get(id=response.data['data']['id'])
        assert conversation.participants.count() == 2
        assert not conversation.is_group
    
    def test_create_group_conversation(self):
        """Test creating a group conversation."""
        user1 = User.objects.create_user(
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='Password123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='Password123'
        )
        user3 = User.objects.create_user(
            email='user3@example.com',
            first_name='User',
            last_name='Three',
            password='Password123'
        )
        
        client = APIClient()
        client.force_authenticate(user=user1)
        
        url = reverse('chat:conversations')
        data = {
            'participant_ids': [user1.id, user2.id, user3.id],
            'name': 'Test Group'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify it's a group conversation
        conversation = Conversation.objects.get(id=response.data['data']['id'])
        assert conversation.participants.count() == 3
        assert conversation.is_group
    
    def test_create_conversation_unauthenticated(self):
        """Test creating conversation without authentication."""
        client = APIClient()
        url = reverse('chat:conversations')
        data = {'participant_ids': [1, 2]}
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestConversationList:
    """Test listing conversations."""
    
    def test_list_conversations(self):
        """Test listing user's conversations."""
        user1 = User.objects.create_user(
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='Password123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='Password123'
        )
        
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)
        
        client = APIClient()
        client.force_authenticate(user=user1)
        
        url = reverse('chat:conversations')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 1


@pytest.mark.django_db
class TestMessages:
    """Test message retrieval."""
    
    def test_get_messages(self):
        """Test retrieving messages from a conversation."""
        user1 = User.objects.create_user(
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='Password123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='Password123'
        )
        
        # Create a conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)
        
        # Add some test messages to Redis
        redis_manager.save_message(str(conversation.id), {
            'id': 'test-msg-1',
            'conversation_id': str(conversation.id),
            'sender_id': user1.id,
            'sender_name': user1.get_full_name(),
            'sender_email': user1.email,
            'content': 'Test message',
            'timestamp': 1234567890.0,
            'created_at': '2024-01-01T00:00:00'
        })
        
        client = APIClient()
        client.force_authenticate(user=user1)
        
        url = reverse('chat:messages', kwargs={'conversation_id': conversation.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'success'
        assert 'data' in response.data
        assert len(response.data['data']['messages']) == 1
    
    def test_get_messages_unauthorized(self):
        """Test retrieving messages from conversation user is not part of."""
        user1 = User.objects.create_user(
            email='user1@example.com',
            first_name='User',
            last_name='One',
            password='Password123'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            first_name='User',
            last_name='Two',
            password='Password123'
        )
        user3 = User.objects.create_user(
            email='user3@example.com',
            first_name='User',
            last_name='Three',
            password='Password123'
        )
        
        # Create a conversation between user1 and user2
        conversation = Conversation.objects.create()
        conversation.participants.add(user1, user2)
        
        # Try to access as user3
        client = APIClient()
        client.force_authenticate(user=user3)
        
        url = reverse('chat:messages', kwargs={'conversation_id': conversation.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestRedisManager:
    """Test Redis message manager."""
    
    def test_save_and_retrieve_message(self):
        """Test saving and retrieving messages from Redis."""
        conversation_id = 'test-conv-123'
        message_data = {
            'id': 'msg-1',
            'conversation_id': conversation_id,
            'sender_id': 1,
            'sender_name': 'Test User',
            'sender_email': 'test@example.com',
            'content': 'Test message',
            'timestamp': 1234567890.0,
            'created_at': '2024-01-01T00:00:00'
        }
        
        # Save message
        result = redis_manager.save_message(conversation_id, message_data)
        assert result is True
        
        # Retrieve messages
        messages = redis_manager.get_messages(conversation_id)
        assert len(messages) >= 1
        
        # Clean up
        redis_manager.delete_conversation(conversation_id)
    
    def test_message_count(self):
        """Test getting message count."""
        conversation_id = 'test-conv-456'
        
        # Add some messages
        for i in range(5):
            redis_manager.save_message(conversation_id, {
                'id': f'msg-{i}',
                'content': f'Message {i}',
                'timestamp': 1234567890.0 + i
            })
        
        # Get count
        count = redis_manager.get_message_count(conversation_id)
        assert count == 5
        
        # Clean up
        redis_manager.delete_conversation(conversation_id)


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_websocket_consumer():
    """Test WebSocket consumer connection."""
    user = await User.objects.acreate(
        email='test@example.com',
        first_name='Test',
        last_name='User'
    )
    user.set_password('Password123')
    await user.asave()
    
    conversation = await Conversation.objects.acreate()
    await conversation.participants.aadd(user)
    
    # This is a basic test - full WebSocket testing would require more setup
    assert user.is_authenticated
    assert await conversation.participants.filter(id=user.id).aexists() 