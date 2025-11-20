import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TermiiService:
    """
    Service for sending SMS via Termii API.
    """
    
    BASE_URL = 'https://api.ng.termii.com/api'
    
    @classmethod
    def send_sms(cls, phone_number, message):
        """
        Send SMS to a phone number.
        
        Args:
            phone_number: Recipient phone number (e.g., 2348012345678)
            message: SMS message content
        
        Returns:
            bool: True if successful, False otherwise
        """
        url = f'{cls.BASE_URL}/sms/send'
        
        # Format phone number (remove + if present)
        phone = phone_number.replace('+', '')
        
        payload = {
            "to": phone,
            "from": settings.TERMII_SENDER_ID,
            "sms": message,
            "type": "plain",
            "channel": "generic",
            "api_key": settings.TERMII_API_KEY
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('message_id'):
                logger.info(f"SMS sent to {phone}: {data.get('message_id')}")
                return True
            else:
                logger.error(f"SMS failed to {phone}: {data}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Termii API error: {str(e)}")
            return False
    
    @classmethod
    def send_verification_code(cls, phone_number, code):
        """
        Send verification code via SMS.
        """
        message = f"Your verification code is: {code}. Valid for 10 minutes. - Internal Logistics Platform"
        return cls.send_sms(phone_number, message)
    
    @classmethod
    def send_order_notification(cls, phone_number, order_number, status):
        """
        Send order notification via SMS.
        """
        message = f"Order #{order_number} status: {status}. Track your delivery at {settings.FRONTEND_URL} - Internal Logistics"
        return cls.send_sms(phone_number, message)
    
    @classmethod
    def send_rider_assignment(cls, phone_number, order_number):
        """
        Notify rider of new assignment.
        """
        message = f"New delivery assigned! Order #{order_number}. Check your app for details. - Internal Logistics"
        return cls.send_sms(phone_number, message)
    
    @classmethod
    def send_delivery_reminder(cls, phone_number, order_number):
        """
        Send delivery reminder to customer.
        """
        message = f"Your order #{order_number} is out for delivery! Expect it soon. - Internal Logistics Platform"
        return cls.send_sms(phone_number, message)
