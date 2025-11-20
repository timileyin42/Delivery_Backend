from django.contrib import admin
from .models import Order, OrderStatusLog


class OrderStatusLogInline(admin.TabularInline):
    """
    Inline display of status logs in order admin.
    """
    model = OrderStatusLog
    extra = 0
    readonly_fields = ['status', 'changed_by', 'notes', 'timestamp']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for Order model.
    """
    list_display = [
        'order_number', 'customer_name', 'status', 'assigned_rider',
        'delivery_fee', 'payment_status', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'customer_email']
    ordering = ['-created_at']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at',
        'assigned_at', 'picked_at', 'delivered_at'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'status', 'payment_status')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Pickup Information', {
            'fields': ('pickup_address', 'pickup_lat', 'pickup_lng')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address', 'delivery_lat', 'delivery_lng')
        }),
        ('Package Details', {
            'fields': ('package_description', 'package_weight')
        }),
        ('Assignment', {
            'fields': ('assigned_rider', 'created_by')
        }),
        ('Financial', {
            'fields': ('delivery_fee',)
        }),
        ('Delivery Proof', {
            'fields': ('delivery_proof_image', 'delivery_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'assigned_at', 'picked_at', 'delivered_at')
        }),
    )
    
    inlines = [OrderStatusLogInline]


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    """
    Admin interface for OrderStatusLog model.
    """
    list_display = ['order', 'status', 'changed_by', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['order__order_number']
    ordering = ['-timestamp']
    readonly_fields = ['order', 'status', 'changed_by', 'notes', 'timestamp']
