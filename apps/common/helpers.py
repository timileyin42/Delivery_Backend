"""
Helper functions for common tasks.
"""
from typing import Optional
import math


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    Returns distance in kilometers.
    """
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def get_client_ip(request) -> str:
    """
    Get client IP address from request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def mask_phone_number(phone: str) -> str:
    """
    Mask phone number for privacy.
    Example: +234801234567 -> +234****4567
    """
    if len(phone) < 8:
        return phone
    return phone[:4] + '****' + phone[-4:]


def get_time_of_day() -> str:
    """
    Get current time of day category.
    """
    from datetime import datetime
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'


def is_location_fresh(last_update, max_age_minutes: int = 5) -> bool:
    """
    Check if location data is recent.
    
    Args:
        last_update: DateTime of last location update
        max_age_minutes: Maximum age in minutes to consider fresh
    
    Returns:
        True if location is fresh, False otherwise
    """
    if not last_update:
        return False
    
    from django.utils import timezone
    from datetime import timedelta
    
    max_age = timedelta(minutes=max_age_minutes)
    return timezone.now() - last_update < max_age


def calculate_eta(distance_km: float, vehicle_type: str = 'MOTORCYCLE') -> dict:
    """
    Calculate estimated time of arrival based on distance and vehicle type.
    
    Args:
        distance_km: Distance in kilometers
        vehicle_type: Type of vehicle (MOTORCYCLE, BICYCLE, CAR, VAN)
    
    Returns:
        Dictionary with ETA information
    """
    # Average speeds by vehicle type (km/h) considering Lagos traffic
    speed_map = {
        'MOTORCYCLE': 25,  # Faster in traffic
        'BICYCLE': 15,
        'CAR': 20,
        'VAN': 18
    }
    
    avg_speed = speed_map.get(vehicle_type, 20)
    
    # Calculate time in minutes
    time_hours = distance_km / avg_speed
    time_minutes = int(time_hours * 60)
    
    # Add buffer time for stops/delays
    time_minutes += 5
    
    # Format human-readable time
    if time_minutes < 5:
        time_text = "Arriving soon"
    elif time_minutes < 60:
        time_text = f"{time_minutes} minutes"
    else:
        hours = time_minutes // 60
        mins = time_minutes % 60
        if mins > 0:
            time_text = f"{hours} hour{'s' if hours > 1 else ''} {mins} minutes"
        else:
            time_text = f"{hours} hour{'s' if hours > 1 else ''}"
    
    return {
        'minutes': time_minutes,
        'text': time_text,
        'distance_km': distance_km,
        'avg_speed_kmh': avg_speed
    }
