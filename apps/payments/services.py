import requests
import hashlib
import hmac
from django.conf import settings
from apps.common.exceptions import PaymentException


class PaystackService:
    """
    Service for Paystack API integration.
    """
    
    BASE_URL = 'https://api.paystack.co'
    
    @classmethod
    def _get_headers(cls):
        return {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def initialize_transaction(cls, email, amount, reference, callback_url=None, metadata=None):
        """
        Initialize a Paystack transaction.
        
        Args:
            email: Customer email
            amount: Amount in kobo (multiply Naira by 100)
            reference: Unique transaction reference
            callback_url: Optional callback URL
            metadata: Optional metadata dict
        
        Returns:
            dict: Paystack response data
        """
        url = f'{cls.BASE_URL}/transaction/initialize'
        
        payload = {
            'email': email,
            'amount': int(amount * 100),  # Convert to kobo
            'reference': reference,
        }
        
        if callback_url:
            payload['callback_url'] = callback_url
        
        if metadata:
            payload['metadata'] = metadata
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=cls._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('status'):
                raise PaymentException(data.get('message', 'Payment initialization failed'))
            
            return data['data']
        
        except requests.RequestException as e:
            raise PaymentException(f'Paystack API error: {str(e)}')
    
    @classmethod
    def verify_transaction(cls, reference):
        """
        Verify a Paystack transaction.
        
        Args:
            reference: Transaction reference to verify
        
        Returns:
            dict: Transaction data
        """
        url = f'{cls.BASE_URL}/transaction/verify/{reference}'
        
        try:
            response = requests.get(
                url,
                headers=cls._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('status'):
                raise PaymentException(data.get('message', 'Transaction verification failed'))
            
            return data['data']
        
        except requests.RequestException as e:
            raise PaymentException(f'Paystack API error: {str(e)}')
    
    @classmethod
    def verify_webhook_signature(cls, payload, signature):
        """
        Verify Paystack webhook signature.
        
        Args:
            payload: Request body (bytes)
            signature: Signature from request headers
        
        Returns:
            bool: True if signature is valid
        """
        hash_value = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            payload,
            hashlib.sha512
        ).hexdigest()
        
        return hash_value == signature
