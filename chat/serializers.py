"""
Serializers for chat models.
"""
from rest_framework import serializers
from .models import Conversation
from users.serializers import UserSerializer


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id',
            'name',
            'participants',
            'participant_ids',
            'display_name',
            'is_group',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display_name(self, obj):
        """Get display name for the conversation."""
        return obj.get_or_create_name()
    
    def validate_participant_ids(self, value):
        """Validate participant IDs."""
        if not value:
            raise serializers.ValidationError("At least one participant is required.")
        
        if len(value) < 2:
            raise serializers.ValidationError("A conversation must have at least 2 participants.")
        
        if len(set(value)) != len(value):
            raise serializers.ValidationError("Duplicate participants are not allowed.")
        
        return value
    
    def create(self, validated_data):
        """Create a new conversation."""
        participant_ids = validated_data.pop('participant_ids')
        is_group = len(participant_ids) > 2
        
        conversation = Conversation.objects.create(
            is_group=is_group,
            **validated_data
        )
        conversation.participants.set(participant_ids)
        
        return conversation


class MessageSerializer(serializers.Serializer):
    """Serializer for chat messages."""
    
    id = serializers.CharField(read_only=True)
    conversation_id = serializers.UUIDField(required=True)
    sender_id = serializers.IntegerField(read_only=True)
    sender_name = serializers.CharField(read_only=True)
    sender_email = serializers.EmailField(read_only=True)
    content = serializers.CharField(required=True, max_length=5000)
    timestamp = serializers.FloatField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    def validate_content(self, value):
        """Validate message content."""
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value.strip() 