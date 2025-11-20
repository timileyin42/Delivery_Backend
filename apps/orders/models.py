from django.db import models
from django.core.validators import MinValueValidator
from apps.users.models import User
from apps.common.utils import generate_order_number


class Order(models.Model):
    """
    Main Order model for delivery management.
    """
    
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        PICKED = 'PICKED', 'Picked Up'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PAID = 'PAID', 'Paid'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'
    
    # Order Details
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Customer Information
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True, null=True)
    
    # Addresses
    pickup_address = models.TextField()
    pickup_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    pickup_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    delivery_address = models.TextField()
    delivery_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    delivery_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    # Package Details
    package_description = models.TextField(blank=True)
    package_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in kg"
    )
    
    # Status and Assignment
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
        db_index=True
    )
    assigned_rider = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        limit_choices_to={'role': 'RIDER'}
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_orders'
    )
    
    # Financial
    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    
    # Delivery Proof
    delivery_proof_image = models.ImageField(
        upload_to='delivery_proofs/',
        null=True,
        blank=True
    )
    delivery_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['assigned_rider', 'status']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.order_number} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Generate order number if not set
        if not self.order_number:
            self.order_number = generate_order_number()
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Check if order is in active state."""
        return self.status not in [
            self.Status.DELIVERED,
            self.Status.FAILED,
            self.Status.CANCELLED
        ]
    
    @property
    def can_be_assigned(self):
        """Check if order can be assigned to a rider."""
        return self.status == self.Status.CREATED
    
    @property
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status not in [
            self.Status.DELIVERED,
            self.Status.FAILED,
            self.Status.CANCELLED
        ]


class OrderStatusLog(models.Model):
    """
    Track order status changes for audit trail.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_logs'
    )
    status = models.CharField(max_length=20, choices=Order.Status.choices)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_status_changes'
    )
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_status_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['order', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status} at {self.timestamp}"
