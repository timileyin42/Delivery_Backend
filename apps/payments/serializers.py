from rest_framework import serializers
from .models import Transaction


class PaymentInitializationSerializer(serializers.Serializer):
    """
    Serializer for initializing payment.
    """
    order_id = serializers.IntegerField()
    email = serializers.EmailField()
    callback_url = serializers.URLField(required=False)
    
    def validate_order_id(self, value):
        from apps.orders.models import Order
        try:
            order = Order.objects.get(pk=value)
            if order.payment_status == Order.PaymentStatus.PAID:
                raise serializers.ValidationError("Order has already been paid for")
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        return value


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for transaction display.
    """
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'order', 'order_number', 'amount',
            'status', 'payment_method', 'paystack_reference',
            'authorization_url', 'metadata', 'created_at', 'paid_at'
        ]
        read_only_fields = fields
