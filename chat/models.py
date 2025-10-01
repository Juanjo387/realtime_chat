"""
Models for the chat application.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Conversation(models.Model):
    """
    Model to store conversation metadata.
    Actual messages are stored in Redis for fast access.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='conversations'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_group = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.name:
            return self.name
        participants_list = list(self.participants.all()[:2])
        if participants_list:
            return f"Conversation: {', '.join([p.get_short_name() for p in participants_list])}"
        return f"Conversation {self.id}"
    
    def get_or_create_name(self):
        """Generate a name for the conversation if not set."""
        if self.name:
            return self.name
        
        participants = list(self.participants.all())
        if self.is_group:
            return f"Group with {', '.join([p.get_short_name() for p in participants[:3]])}"
        elif len(participants) == 2:
            return f"Chat with {participants[0].get_short_name()} and {participants[1].get_short_name()}"
        return "Conversation" 