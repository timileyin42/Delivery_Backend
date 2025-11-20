import random
import string
from datetime import datetime
from typing import Any, Dict


def generate_order_number() -> str:
    """
    Generate unique order number with format: ORD-YYYYMMDD-XXXX
    where XXXX is a random 4-digit number.
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"ORD-{date_str}-{random_suffix}"


def generate_transaction_reference() -> str:
    """
    Generate unique transaction reference.
    Format: TXN-TIMESTAMP-RANDOM
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TXN-{timestamp}-{random_suffix}"


def format_phone_number(phone: str) -> str:
    """
    Format phone number to standard Nigerian format.
    Converts to +234XXXXXXXXXX format.
    """
    # Remove all non-numeric characters
    phone = ''.join(filter(str.isdigit, phone))
    
    # Handle different formats
    if phone.startswith('234'):
        return f"+{phone}"
    elif phone.startswith('0'):
        return f"+234{phone[1:]}"
    elif len(phone) == 10:
        return f"+234{phone}"
    else:
        return phone


def success_response(data: Any = None, message: str = "Success") -> Dict:
    """
    Standard success response format.
    """
    return {
        "status": "success",
        "message": message,
        "data": data
    }


def error_response(message: str, errors: Any = None) -> Dict:
    """
    Standard error response format.
    """
    response = {
        "status": "error",
        "message": message
    }
    if errors:
        response["errors"] = errors
    return response


def calculate_delivery_fee(distance_km: float) -> float:
    """
    Calculate delivery fee based on distance.
    Base fee: ₦500
    Additional: ₦100 per km after first 2km
    """
    base_fee = 500
    base_distance = 2
    per_km_rate = 100
    
    if distance_km <= base_distance:
        return base_fee
    
    additional_distance = distance_km - base_distance
    additional_fee = additional_distance * per_km_rate
    
    return base_fee + additional_fee


def calculate_rider_earnings(delivery_fee: float) -> float:
    """
    Calculate rider earnings from delivery fee.
    Rider gets 70% of the delivery fee.
    """
    rider_percentage = 0.70
    return delivery_fee * rider_percentage
