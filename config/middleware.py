import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all API requests and responses.
    """
    
    def process_request(self, request):
        """Log incoming request."""
        request.start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.path} "
            f"User: {request.user if hasattr(request, 'user') else 'Anonymous'}"
        )
        
    def process_response(self, request, response):
        """Log response details."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(
                f"Response: {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.2f}s"
            )
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions."""
        logger.error(
            f"Exception: {request.method} {request.path} "
            f"Error: {str(exception)}",
            exc_info=True
        )
        return None
