"""
Redis manager for message storage.
Messages are stored in Redis for fast access and retrieval.
"""
import redis
import json
from django.conf import settings
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger('chat')


class RedisMessageManager:
    """Manager for storing and retrieving messages from Redis."""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    
    def _get_conversation_key(self, conversation_id: str) -> str:
        """Generate Redis key for a conversation."""
        return f"conversation:{conversation_id}:messages"
    
    def _get_unread_key(self, conversation_id: str, user_id: int) -> str:
        """Generate Redis key for unread message count."""
        return f"conversation:{conversation_id}:user:{user_id}:unread"
    
    def save_message(self, conversation_id: str, message_data: Dict) -> bool:
        """
        Save a message to Redis.
        Messages are stored in a sorted set with timestamp as score.
        """
        try:
            key = self._get_conversation_key(conversation_id)
            score = message_data.get('timestamp', datetime.now().timestamp())
            
            # Store message as JSON
            message_json = json.dumps(message_data)
            
            # Add to sorted set (allows retrieval by time)
            self.redis_client.zadd(key, {message_json: score})
            
            # Set expiry for the conversation (24 hours by default)
            self.redis_client.expire(key, settings.MESSAGE_EXPIRY)
            
            logger.debug(f"Message saved to Redis: conversation={conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving message to Redis: {str(e)}")
            return False
    
    def get_messages(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Retrieve messages for a conversation.
        Returns messages in chronological order (oldest first).
        """
        try:
            key = self._get_conversation_key(conversation_id)
            
            # Get messages from sorted set (oldest first)
            # offset to (offset + limit - 1)
            messages_json = self.redis_client.zrange(
                key,
                offset,
                offset + limit - 1
            )
            
            messages = [json.loads(msg) for msg in messages_json]
            logger.debug(f"Retrieved {len(messages)} messages from Redis: conversation={conversation_id}")
            
            return messages
        except Exception as e:
            logger.error(f"Error retrieving messages from Redis: {str(e)}")
            return []
    
    def get_latest_messages(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get the latest N messages from a conversation.
        Returns messages in chronological order (oldest first).
        """
        try:
            key = self._get_conversation_key(conversation_id)
            
            # Get latest messages (using negative indices for newest)
            messages_json = self.redis_client.zrange(
                key,
                -limit,
                -1
            )
            
            messages = [json.loads(msg) for msg in messages_json]
            logger.debug(f"Retrieved {len(messages)} latest messages from Redis: conversation={conversation_id}")
            
            return messages
        except Exception as e:
            logger.error(f"Error retrieving latest messages from Redis: {str(e)}")
            return []
    
    def get_message_count(self, conversation_id: str) -> int:
        """Get total message count for a conversation."""
        try:
            key = self._get_conversation_key(conversation_id)
            count = self.redis_client.zcard(key)
            return count
        except Exception as e:
            logger.error(f"Error getting message count from Redis: {str(e)}")
            return 0
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete all messages for a conversation."""
        try:
            key = self._get_conversation_key(conversation_id)
            self.redis_client.delete(key)
            logger.info(f"Conversation deleted from Redis: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation from Redis: {str(e)}")
            return False
    
    def increment_unread_count(self, conversation_id: str, user_id: int) -> int:
        """Increment unread message count for a user in a conversation."""
        try:
            key = self._get_unread_key(conversation_id, user_id)
            count = self.redis_client.incr(key)
            self.redis_client.expire(key, settings.MESSAGE_EXPIRY)
            return count
        except Exception as e:
            logger.error(f"Error incrementing unread count: {str(e)}")
            return 0
    
    def reset_unread_count(self, conversation_id: str, user_id: int) -> bool:
        """Reset unread message count for a user in a conversation."""
        try:
            key = self._get_unread_key(conversation_id, user_id)
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error resetting unread count: {str(e)}")
            return False
    
    def get_unread_count(self, conversation_id: str, user_id: int) -> int:
        """Get unread message count for a user in a conversation."""
        try:
            key = self._get_unread_key(conversation_id, user_id)
            count = self.redis_client.get(key)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return 0


# Singleton instance
redis_manager = RedisMessageManager() 