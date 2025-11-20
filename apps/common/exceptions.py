from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from .utils import error_response


class CustomAPIException(APIException):
    """
    Base custom exception for API errors.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred.'
    default_code = 'error'


class ValidationException(CustomAPIException):
    """Exception for validation errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation error.'


class NotFoundException(CustomAPIException):
    """Exception for resource not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'


class PermissionDeniedException(CustomAPIException):
    """Exception for permission denied."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'


class AuthenticationException(CustomAPIException):
    """Exception for authentication errors."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed.'


class PaymentException(CustomAPIException):
    """Exception for payment-related errors."""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment error occurred.'


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF.
    Returns errors in consistent format.
    """
    # Call DRF's default handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response data
        custom_response_data = error_response(
            message=str(exc),
            errors=response.data if isinstance(response.data, dict) else {'detail': response.data}
        )
        response.data = custom_response_data
    
    return response
