"""
WebSocket consumers for real-time chat.
"""
import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import datetime
import logging

from .models import Conversation
from .redis_manager import redis_manager
from users.models import User

logger = logging.getLogger('chat')


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat messaging."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            logger.warning(f"Unauthenticated connection attempt to conversation {self.conversation_id}")
            await self.close()
            return
        
        # Verify user is participant in the conversation
        is_participant = await self.verify_participant()
        if not is_participant:
            logger.warning(
                f"User {self.user.id} attempted to connect to conversation {self.conversation_id} without permission"
            )
            await self.close()
            return
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"User {self.user.id} connected to conversation {self.conversation_id}")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat',
            'conversation_id': str(self.conversation_id)
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave conversation group
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )
        
        logger.info(f"User {self.user.id} disconnected from conversation {self.conversation_id}")
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read':
                await self.handle_read_receipt(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received from user {self.user.id}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred processing your message'
            }))
    
    async def handle_chat_message(self, data):
        """Handle chat message."""
        content = data.get('content', '').strip()
        
        if not content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content cannot be empty'
            }))
            return
        
        # Create message data
        message_id = str(uuid.uuid4())
        timestamp = datetime.now().timestamp()
        
        message_data = {
            'id': message_id,
            'conversation_id': str(self.conversation_id),
            'sender_id': self.user.id,
            'sender_name': self.user.get_full_name(),
            'sender_email': self.user.email,
            'content': content,
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat()
        }
        
        # Save message to Redis
        await database_sync_to_async(redis_manager.save_message)(
            str(self.conversation_id),
            message_data
        )
        
        # Update conversation timestamp
        await self.update_conversation_timestamp()
        
        # Broadcast message to conversation group
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message_data
            }
        )
        
        logger.info(f"Message sent in conversation {self.conversation_id} by user {self.user.id}")
    
    async def handle_typing(self, data):
        """Handle typing indicator."""
        is_typing = data.get('is_typing', False)
        
        # Broadcast typing status to others in the conversation
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'user_name': self.user.get_full_name(),
                'is_typing': is_typing
            }
        )
    
    async def handle_read_receipt(self, data):
        """Handle read receipt."""
        # Reset unread count for this user
        await database_sync_to_async(redis_manager.reset_unread_count)(
            str(self.conversation_id),
            self.user.id
        )
    
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        message = event['message']
        
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))
    
    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))
    
    @database_sync_to_async
    def verify_participant(self):
        """Verify that the user is a participant in the conversation."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def update_conversation_timestamp(self):
        """Update the conversation's updated_at timestamp."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            conversation.updated_at = timezone.now()
            conversation.save(update_fields=['updated_at'])
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {self.conversation_id} not found") 