import resend
from django.conf import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

# Set Resend API key
resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """
    Service for sending emails via Resend using Django templates.
    """
    
    FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    
    @classmethod
    def send_verification_email(cls, user, verification_token):
        """
        Send email verification link to user.
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        context = {
            'user_name': user.first_name,
            'verification_url': verification_url,
        }
        
        html_content = render_to_string('emails/verification_email.html', context)
        
        try:
            params = {
                "from": cls.FROM_EMAIL,
                "to": [user.email],
                "subject": "Verify Your Email - Internal Logistics Platform",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Verification email sent to {user.email}: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            return False
    
    @classmethod
    def send_welcome_email(cls, user):
        """
        Send welcome email after successful verification.
        """
        context = {
            'user_name': user.first_name,
            'dashboard_url': f"{settings.FRONTEND_URL}/login",
        }
        
        html_content = render_to_string('emails/welcome_email.html', context)
        
        try:
            params = {
                "from": cls.FROM_EMAIL,
                "to": [user.email],
                "subject": "Welcome to Internal Logistics Platform!",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Welcome email sent to {user.email}: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False
    
    @classmethod
    def send_password_reset_email(cls, user, reset_token):
        """
        Send password reset link to user.
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        context = {
            'user_name': user.first_name,
            'reset_url': reset_url,
        }
        
        html_content = render_to_string('emails/password_reset.html', context)
        
        try:
            params = {
                "from": cls.FROM_EMAIL,
                "to": [user.email],
                "subject": "Reset Your Password - Internal Logistics Platform",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Password reset email sent to {user.email}: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False
    
    @classmethod
    def send_order_notification_email(cls, user, order, notification_message):
        """
        Send order-related notification emails.
        """
        context = {
            'user_name': user.first_name,
            'notification_message': notification_message,
            'order_number': order.order_number,
            'order_status': order.get_status_display(),
            'delivery_address': order.delivery_address,
            'delivery_fee': order.delivery_fee,
        }
        
        html_content = render_to_string('emails/order_notification.html', context)
        
        try:
            params = {
                "from": cls.FROM_EMAIL,
                "to": [user.email],
                "subject": f"Order Update - #{order.order_number}",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            logger.info(f"Order notification email sent to {user.email}: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order notification to {user.email}: {str(e)}")
            return False
