from rest_framework import serializers
from .models import Order, OrderStatusLog
from apps.users.serializers import UserSerializer
from apps.riders.serializers import RiderProfileSerializer


class OrderStatusLogSerializer(serializers.ModelSerializer):
    """
    Serializer for order status logs.
    """
    changed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderStatusLog
        fields = ['id', 'status', 'changed_by', 'changed_by_name', 'notes', 'timestamp']
        read_only_fields = fields
    
    def get_changed_by_name(self, obj):
        return obj.changed_by.get_full_name() if obj.changed_by else "System"


class OrderSerializer(serializers.ModelSerializer):
    """
    Base serializer for Order model.
    """
    assigned_rider_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    is_active = serializers.ReadOnlyField()
    can_be_assigned = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_phone', 'customer_email',
            'pickup_address', 'pickup_lat', 'pickup_lng',
            'delivery_address', 'delivery_lat', 'delivery_lng',
            'package_description', 'package_weight',
            'status', 'assigned_rider', 'assigned_rider_name',
            'created_by', 'created_by_name',
            'delivery_fee', 'payment_status',
            'delivery_proof_image', 'delivery_notes',
            'created_at', 'updated_at', 'assigned_at', 'picked_at', 'delivered_at',
            'is_active', 'can_be_assigned', 'can_be_cancelled'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at',
            'assigned_at', 'picked_at', 'delivered_at'
        ]
    
    def get_assigned_rider_name(self, obj):
        return obj.assigned_rider.get_full_name() if obj.assigned_rider else None
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new orders.
    """
    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_phone', 'customer_email',
            'pickup_address', 'pickup_lat', 'pickup_lng',
            'delivery_address', 'delivery_lat', 'delivery_lng',
            'package_description', 'package_weight', 'delivery_fee'
        ]
    
    def create(self, validated_data):
        # Add created_by from request context
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for order with nested data.
    """
    assigned_rider_details = RiderProfileSerializer(
        source='assigned_rider.rider_profile',
        read_only=True
    )
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_phone', 'customer_email',
            'pickup_address', 'pickup_lat', 'pickup_lng',
            'delivery_address', 'delivery_lat', 'delivery_lng',
            'package_description', 'package_weight',
            'status', 'assigned_rider', 'assigned_rider_details',
            'created_by', 'created_by_details',
            'delivery_fee', 'payment_status',
            'delivery_proof_image', 'delivery_notes',
            'created_at', 'updated_at', 'assigned_at', 'picked_at', 'delivered_at',
            'status_logs'
        ]


class OrderAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning order to rider.
    """
    rider_id = serializers.IntegerField(required=True)
    
    def validate_rider_id(self, value):
        from apps.users.models import User
        try:
            rider = User.objects.get(id=value, role=User.Role.RIDER)
            if not hasattr(rider, 'rider_profile'):
                raise serializers.ValidationError("User is not a valid rider.")
            if not rider.rider_profile.is_available:
                raise serializers.ValidationError("Rider is not available.")
            if rider.rider_profile.status != 'ACTIVE':
                raise serializers.ValidationError("Rider is not active.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Rider not found.")
        return value


class OrderStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating order status.
    """
    status = serializers.ChoiceField(choices=Order.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    delivery_proof_image = serializers.ImageField(required=False, allow_null=True)
    
    def validate_status(self, value):
        order = self.context.get('order')
        current_status = order.status
        
        # Define valid status transitions
        valid_transitions = {
            Order.Status.CREATED: [Order.Status.ASSIGNED, Order.Status.CANCELLED],
            Order.Status.ASSIGNED: [Order.Status.ACCEPTED, Order.Status.CANCELLED],
            Order.Status.ACCEPTED: [Order.Status.PICKED, Order.Status.FAILED],
            Order.Status.PICKED: [Order.Status.IN_TRANSIT, Order.Status.FAILED],
            Order.Status.IN_TRANSIT: [Order.Status.DELIVERED, Order.Status.FAILED],
        }
        
        if current_status not in valid_transitions:
            raise serializers.ValidationError(
                f"Cannot update status from {current_status}"
            )
        
        if value not in valid_transitions[current_status]:
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}"
            )
        
        return value
