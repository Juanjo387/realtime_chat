"""
URL patterns for chat app.
"""
from django.urls import path
from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    ConversationMessagesView,
    HealthCheckView,
)

app_name = 'chat'

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('conversations/', ConversationListCreateView.as_view(), name='conversations'),
    path('conversations/<uuid:id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<uuid:conversation_id>/messages/', ConversationMessagesView.as_view(), name='messages'),
] 