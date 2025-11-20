from rest_framework import serializers
from .models import RiderProfile, RiderEarnings
from apps.users.serializers import UserSerializer
from apps.orders.models import Order


class RiderProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for RiderProfile model.
    """
    user = UserSerializer(read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = RiderProfile
        fields = [
            'id', 'user', 'vehicle_type', 'vehicle_model', 'vehicle_plate_number',
            'license_number', 'status', 'rating', 'total_deliveries',
            'successful_deliveries', 'failed_deliveries', 'success_rate',
            'total_earnings', 'is_available', 'current_location_lat',
            'current_location_lng', 'onboarding_completed', 'documents_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'rating', 'total_deliveries', 'successful_deliveries',
            'failed_deliveries', 'total_earnings', 'created_at', 'updated_at'
        ]


class RiderProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating rider profile (riders can update their own).
    """
    class Meta:
        model = RiderProfile
        fields = [
            'vehicle_type', 'vehicle_model', 'vehicle_plate_number',
            'license_number', 'is_available', 'current_location_lat',
            'current_location_lng'
        ]


class RiderTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for rider's assigned tasks (orders).
    """
    customer_name = serializers.CharField(source='order.customer_name', read_only=True)
    customer_phone = serializers.CharField(source='order.customer_phone', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_phone',
            'pickup_address', 'delivery_address', 'status', 'delivery_fee',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class RiderEarningsSerializer(serializers.ModelSerializer):
    """
    Serializer for rider earnings.
    """
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = RiderEarnings
        fields = [
            'id', 'order', 'order_number', 'amount', 'delivery_fee', 'earned_at'
        ]
        read_only_fields = fields


class RiderPerformanceSerializer(serializers.Serializer):
    """
    Serializer for rider performance metrics.
    """
    total_deliveries = serializers.IntegerField()
    successful_deliveries = serializers.IntegerField()
    failed_deliveries = serializers.IntegerField()
    success_rate = serializers.FloatField()
    total_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    deliveries_this_week = serializers.IntegerField()
    earnings_this_week = serializers.DecimalField(max_digits=12, decimal_places=2)
    deliveries_this_month = serializers.IntegerField()
    earnings_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
