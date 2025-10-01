"""
Views for chat application.
"""
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from django.db import transaction
from django.db.models import Q
import logging

from .models import Conversation
from .serializers import ConversationSerializer, MessageSerializer
from .redis_manager import redis_manager
from .throttling import MessageRateThrottle

logger = logging.getLogger('api')


class ConversationListCreateView(generics.ListCreateAPIView):
    """API endpoint for listing and creating conversations."""
    
    serializer_class = ConversationSerializer
    
    def get_queryset(self):
        """Return conversations where user is a participant."""
        if self.request.user.is_authenticated:
            return Conversation.objects.filter(
                participants=self.request.user
            ).prefetch_related('participants')
        return Conversation.objects.none()
    
    def list(self, request, *args, **kwargs):
        """List all conversations for the authenticated user."""
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Add message counts and unread counts
        conversations_data = []
        for conv_data, conv in zip(serializer.data, queryset):
            conv_data['message_count'] = redis_manager.get_message_count(str(conv.id))
            conv_data['unread_count'] = redis_manager.get_unread_count(
                str(conv.id),
                request.user.id
            )
            conversations_data.append(conv_data)
        
        logger.info(f"User {request.user.id} listed conversations")
        
        return Response({
            'status': 'success',
            'data': conversations_data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """Create a new conversation."""
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Add current user to participants if not already included
        participant_ids = request.data.get('participant_ids', [])
        if request.user.id not in participant_ids:
            participant_ids.append(request.user.id)
        
        # Check if conversation already exists (for non-group chats)
        if len(participant_ids) == 2:
            existing_conv = Conversation.objects.filter(
                is_group=False
            ).filter(
                participants__id=participant_ids[0]
            ).filter(
                participants__id=participant_ids[1]
            ).first()
            
            if existing_conv:
                logger.info(f"Returning existing conversation {existing_conv.id}")
                return Response({
                    'status': 'success',
                    'message': 'Conversation already exists',
                    'data': ConversationSerializer(existing_conv).data
                }, status=status.HTTP_200_OK)
        
        # Create new conversation
        data = request.data.copy()
        data['participant_ids'] = participant_ids
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    conversation = serializer.save()
                    logger.info(f"Conversation created: {conversation.id} by user {request.user.id}")
                    
                    return Response({
                        'status': 'success',
                        'message': 'Conversation created successfully',
                        'data': ConversationSerializer(conversation).data
                    }, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating conversation: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': 'An error occurred while creating the conversation'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.warning(f"Conversation creation validation failed: {serializer.errors}")
        return Response({
            'status': 'error',
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ConversationDetailView(generics.RetrieveAPIView):
    """API endpoint for retrieving conversation details."""
    
    serializer_class = ConversationSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return conversations where user is a participant."""
        if self.request.user.is_authenticated:
            return Conversation.objects.filter(
                participants=self.request.user
            ).prefetch_related('participants')
        return Conversation.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve conversation details."""
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            conversation = self.get_object()
            serializer = self.get_serializer(conversation)
            
            data = serializer.data
            data['message_count'] = redis_manager.get_message_count(str(conversation.id))
            data['unread_count'] = redis_manager.get_unread_count(
                str(conversation.id),
                request.user.id
            )
            
            logger.info(f"User {request.user.id} retrieved conversation {conversation.id}")
            
            return Response({
                'status': 'success',
                'data': data
            }, status=status.HTTP_200_OK)
        except Conversation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ConversationMessagesView(APIView):
    """API endpoint for retrieving messages from a conversation."""
    
    throttle_classes = [MessageRateThrottle]
    
    def get(self, request, conversation_id):
        """Retrieve messages for a conversation."""
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verify user is participant
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            if not conversation.participants.filter(id=request.user.id).exists():
                logger.warning(
                    f"User {request.user.id} attempted to access conversation {conversation_id} without permission"
                )
                return Response({
                    'status': 'error',
                    'message': 'You are not a participant in this conversation'
                }, status=status.HTTP_403_FORBIDDEN)
        except Conversation.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get pagination parameters
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 50
        if offset < 0:
            offset = 0
        
        # Retrieve messages from Redis
        messages = redis_manager.get_latest_messages(
            str(conversation_id),
            limit=limit
        )
        
        # Reset unread count
        redis_manager.reset_unread_count(str(conversation_id), request.user.id)
        
        logger.info(
            f"User {request.user.id} retrieved {len(messages)} messages from conversation {conversation_id}"
        )
        
        return Response({
            'status': 'success',
            'data': {
                'conversation_id': str(conversation_id),
                'messages': messages,
                'count': len(messages),
                'total': redis_manager.get_message_count(str(conversation_id))
            }
        }, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    """Health check endpoint."""
    
    def get(self, request):
        """Return health status."""
        return Response({
            'status': 'success',
            'message': 'API is running'
        }, status=status.HTTP_200_OK) 