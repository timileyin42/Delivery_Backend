from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils import timezone

from apps.common.models import EmailVerificationToken, PasswordResetToken
from apps.common.email_service import EmailService
from apps.common.utils import success_response, error_response
from .models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    """
    Verify user email with token.
    POST /api/users/verify-email/
    Body: {"token": "..."}
    """
    token_str = request.data.get('token')
    
    if not token_str:
        return Response(
            error_response(message="Token is required"),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = EmailVerificationToken.objects.get(token=token_str)
        
        if not token.is_valid:
            return Response(
                error_response(message="Token is invalid or expired"),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark user as verified
        user = token.user
        user.email_verified = True
        user.save()
        
        # Mark token as used  
        token.is_used = True
        token.save()
        
        # Send welcome email
        EmailService.send_welcome_email(user)
        
        return Response(
            success_response(
                message="Email verified successfully! You can now log in."
            ),
            status=status.HTTP_200_OK
        )
        
    except EmailVerificationToken.DoesNotExist:
        return Response(
            error_response(message="Invalid token"),
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email_view(request):
    """
    Resend verification email.
    POST /api/users/resend-verification/
    Body: {"email": "..."}
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            error_response(message="Email is required"),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        if user.email_verified:
            return Response(
                error_response(message="Email is already verified"),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new verification token
        token = EmailVerificationToken.objects.create(user=user)
        
        # Send verification email
        EmailService.send_verification_email(user, token.token)
        
        return Response(
            success_response(
                message="Verification email sent successfully"
            ),
            status=status.HTTP_200_OK
        )
        
    except User.DoesNotExist:
        return Response(
            error_response(message="User with this email not found"),
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_password_reset_view(request):
    """
    Initiate password reset - creates token and sends email.
    POST /api/users/initiate-reset/
    Body: {"email": "..."}
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            error_response(message="Email is required"),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        
        # Create reset token
        token = PasswordResetToken.objects.create(user=user)
        
        # Send reset email
        EmailService.send_password_reset_email(user, token.token)
        
        return Response(
            success_response(
                message="Password reset email sent successfully"
            ),
            status=status.HTTP_200_OK
        )
        
    except User.DoesNotExist:
        # Don't reveal that user doesn't exist (security)
        return Response(
            success_response(
                message="If an account exists with this email, a password reset link has been sent"
            ),
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset_view(request):
    """
    Confirm password reset with token and new password.
    POST /api/users/confirm-reset/
    Body: {"token": "...", "new_password": "..."}
    """
    token_str = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not token_str or not new_password:
        return Response(
            error_response(message="Token and new password are required"),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = PasswordResetToken.objects.get(token=token_str)
        
        if not token.is_valid:
            return Response(
                error_response(message="Token is invalid or expired"),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update password
        user = token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        token.is_used = True
        token.save()
        
        return Response(
            success_response(
                message="Password reset successfully. You can now log in with your new password."
            ),
            status=status.HTTP_200_OK
        )
        
    except PasswordResetToken.DoesNotExist:
        return Response(
            error_response(message="Invalid token"),
            status=status.HTTP_404_NOT_FOUND
        )
