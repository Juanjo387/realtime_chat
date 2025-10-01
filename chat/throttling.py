"""
Custom throttling classes for rate limiting.
"""
from rest_framework.throttling import UserRateThrottle


class MessageRateThrottle(UserRateThrottle):
    """
    Throttle for message-related endpoints.
    Limits users to 10 requests per minute.
    """
    scope = 'message'
    rate = '10/minute' 