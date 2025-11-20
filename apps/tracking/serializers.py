from rest_framework import serializers
from .models import RiderLocation


class LocationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for rider location updates.
    """
    class Meta:
        model = RiderLocation
        fields = ['latitude', 'longitude', 'accuracy', 'speed', 'heading', 'order']
        
    def create(self, validated_data):
        # Add rider from request context
        validated_data['rider'] = self.context['request'].user
        return super().create(validated_data)


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for location display.
    """
    rider_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RiderLocation
        fields = [
            'id', 'rider', 'rider_name', 'order', 'latitude', 'longitude',
            'accuracy', 'speed', 'heading', 'timestamp'
        ]
        read_only_fields = fields
    
    def get_rider_name(self, obj):
        return obj.rider.get_full_name()
