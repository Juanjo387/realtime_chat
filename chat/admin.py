"""
Admin configuration for chat app.
"""
from django.contrib import admin
from .models import Conversation


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model."""
    
    list_display = ['id', 'name', 'is_group', 'created_at', 'updated_at', 'participant_count']
    list_filter = ['is_group', 'created_at']
    search_fields = ['id', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['participants']
    
    def participant_count(self, obj):
        """Return the number of participants."""
        return obj.participants.count()
    
    participant_count.short_description = 'Participants' 