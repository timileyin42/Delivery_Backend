from rest_framework import serializers
from django.utils import timezone
from .models import RiderProfile
from apps.orders.models import Order
from apps.common.helpers import calculate_distance


class RiderLocationUpdateSerializer(serializers.Serializer):
    """
    Serializer for riders to update their location.
    POST /api/riders/location/update/
    """
    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=True,
        help_text="Latitude coordinate"
    )
    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=True,
        help_text="Longitude coordinate"
    )

    def validate_latitude(self, value):
        """Validate latitude is within valid range."""
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90")
        return value

    def validate_longitude(self, value):
        """Validate longitude is within valid range."""
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180")
        return value

    def update_location(self, rider_profile):
        """Update rider's location."""
        rider_profile.current_location_lat = self.validated_data['latitude']
        rider_profile.current_location_lng = self.validated_data['longitude']
        rider_profile.last_location_update = timezone.now()
        rider_profile.save(update_fields=[
            'current_location_lat',
            'current_location_lng',
            'last_location_update'
        ])
        return rider_profile


class RiderLocationSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing rider's current location.
    Used in order tracking.
    """
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    phone = serializers.SerializerMethodField()
    is_fresh = serializers.BooleanField(source='is_location_fresh', read_only=True)
    
    class Meta:
        model = RiderProfile
        fields = [
            'name',
            'phone',
            'vehicle_type',
            'rating',
            'current_location_lat',
            'current_location_lng',
            'last_location_update',
            'is_fresh'
        ]
    
    def get_phone(self, obj):
        """Mask phone number for privacy (show last 2 digits)."""
        phone = obj.user.phone
        if phone and len(phone) >= 4:
            return phone[:-4] + '****' + phone[-2:]
        return phone


class OrderTrackingSerializer(serializers.ModelSerializer):
    """
    Complete order tracking information with rider location.
    GET /api/orders/{id}/track/
    """
    rider = serializers.SerializerMethodField()
    estimated_arrival = serializers.SerializerMethodField()
    distance_remaining = serializers.SerializerMethodField()
    pickup_coordinates = serializers.SerializerMethodField()
    delivery_coordinates = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'order_number',
            'status',
            'rider',
            'pickup_address',
            'delivery_address',
            'pickup_coordinates',
            'delivery_coordinates',
            'estimated_arrival',
            'distance_remaining',
            'created_at'
        ]
    
    def get_rider(self, obj):
        """Get rider information with current location."""
        if not obj.rider:
            return None
        
        # Only show location if order is in active delivery status
        active_statuses = ['ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']
        if obj.status not in active_statuses:
            return {
                'name': obj.rider.user.get_full_name(),
                'phone': self._mask_phone(obj.rider.user.phone),
                'vehicle_type': obj.rider.vehicle_type,
                'rating': float(obj.rider.rating),
                'location_available': False
            }
        
        serializer = RiderLocationSerializer(obj.rider)
        data = serializer.data
        data['location_available'] = True
        return data
    
    def get_pickup_coordinates(self, obj):
        """Get pickup location coordinates."""
        if obj.pickup_lat and obj.pickup_lng:
            return {
                'latitude': float(obj.pickup_lat),
                'longitude': float(obj.pickup_lng)
            }
        return None
    
    def get_delivery_coordinates(self, obj):
        """Get delivery location coordinates."""
        if obj.delivery_lat and obj.delivery_lng:
            return {
                'latitude': float(obj.delivery_lat),
                'longitude': float(obj.delivery_lng)
            }
        return None
    
    def get_distance_remaining(self, obj):
        """Calculate distance from rider to delivery address."""
        if not obj.rider or not obj.rider.current_location_lat:
            return None
        
        if not obj.delivery_lat or not obj.delivery_lng:
            return None
        
        # Calculate distance from rider's current location to delivery address
        distance_km = calculate_distance(
            float(obj.rider.current_location_lat),
            float(obj.rider.current_location_lng),
            float(obj.delivery_lat),
            float(obj.delivery_lng)
        )
        
        return {
            'kilometers': round(distance_km, 2),
            'meters': round(distance_km * 1000, 0)
        }
    
    def get_estimated_arrival(self, obj):
        """Calculate estimated arrival time based on distance and vehicle type."""
        distance_info = self.get_distance_remaining(obj)
        if not distance_info:
            return None
        
        distance_km = distance_info['kilometers']
        
        # Average speeds by vehicle type (km/h) considering Lagos traffic
        speed_map = {
            'MOTORCYCLE': 25,  # Faster in traffic
            'BICYCLE': 15,
            'CAR': 20,
            'VAN': 18
        }
        
        vehicle_type = obj.rider.vehicle_type if obj.rider else 'MOTORCYCLE'
        avg_speed = speed_map.get(vehicle_type, 20)
        
        # Calculate time in minutes
        time_hours = distance_km / avg_speed
        time_minutes = int(time_hours * 60)
        
        # Add buffer time for stops/delays
        time_minutes += 5
        
        if time_minutes < 5:
            return "Arriving soon"
        elif time_minutes < 60:
            return f"{time_minutes} minutes"
        else:
            hours = time_minutes // 60
            mins = time_minutes % 60
            if mins > 0:
                return f"{hours} hour{'s' if hours > 1 else ''} {mins} minutes"
            return f"{hours} hour{'s' if hours > 1 else ''}"
    
    def _mask_phone(self, phone):
        """Helper to mask phone number."""
        if phone and len(phone) >= 4:
            return phone[:-4] + '****' + phone[-2:]
        return phone


class AdminRiderLocationSerializer(serializers.ModelSerializer):
    """
    Admin view of rider location (full details).
    GET /api/riders/{id}/location/
    """
    rider_name = serializers.CharField(source='user.get_full_name', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    is_fresh = serializers.BooleanField(source='is_location_fresh', read_only=True)
    active_orders = serializers.SerializerMethodField()
    
    class Meta:
        model = RiderProfile
        fields = [
            'id',
            'rider_name',
            'phone',
            'vehicle_type',
            'vehicle_plate_number',
            'status',
            'is_available',
            'current_location_lat',
            'current_location_lng',
            'last_location_update',
            'is_fresh',
            'active_orders'
        ]
    
    def get_active_orders(self, obj):
        """Get list of active orders for this rider."""
        active_orders = Order.objects.filter(
            rider=obj,
            status__in=['ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']
        ).values('order_number', 'status', 'delivery_address')
        return list(active_orders)
