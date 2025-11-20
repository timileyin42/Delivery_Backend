from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notifications.
    """
    related_order_number = serializers.CharField(
        source='related_order.order_number',
        read_only=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'is_read',
            'related_order', 'related_order_number', 'created_at', 'read_at'
        ]
        read_only_fields = fields
