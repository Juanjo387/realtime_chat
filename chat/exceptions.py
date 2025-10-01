"""
Custom exception handlers for the chat application.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('api')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats errors consistently
    and logs them appropriately.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    request = context.get('request')
    if request:
        logger.error(
            f"Exception in API: {exc.__class__.__name__} - {str(exc)} "
            f"- Path: {request.path} - User: {request.user.id if request.user.is_authenticated else 'anonymous'}"
        )
    
    # If response is None, it means the exception wasn't handled by DRF
    if response is None:
        logger.error(f"Unhandled exception: {exc.__class__.__name__} - {str(exc)}")
        return Response({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'detail': str(exc)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Format the response consistently
    error_data = {
        'status': 'error',
        'message': 'Request failed',
    }
    
    # Handle different types of errors
    if hasattr(response, 'data'):
        if isinstance(response.data, dict):
            # Extract error details
            if 'detail' in response.data:
                error_data['message'] = response.data['detail']
            else:
                error_data['errors'] = response.data
        elif isinstance(response.data, list):
            error_data['message'] = response.data[0] if response.data else 'Request failed'
        else:
            error_data['message'] = str(response.data)
    
    response.data = error_data
    
    return response 