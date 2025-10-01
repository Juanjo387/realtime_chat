"""
Custom middleware for the chat application.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api')


class APILoggingMiddleware(MiddlewareMixin):
    """Middleware to log all API requests."""
    
    def process_request(self, request):
        """Log incoming requests."""
        request.start_time = time.time()
        
        # Log API request
        log_data = {
            'method': request.method,
            'path': request.path,
            'user': request.user.id if request.user.is_authenticated else 'anonymous',
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown')
        }
        
        logger.info(
            f"API Request: {log_data['method']} {log_data['path']} "
            f"- User: {log_data['user']} - IP: {log_data['ip']}"
        )
        
        return None
    
    def process_response(self, request, response):
        """Log response details."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            logger.info(
                f"API Response: {request.method} {request.path} "
                f"- Status: {response.status_code} - Duration: {duration:.3f}s"
            )
        
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 