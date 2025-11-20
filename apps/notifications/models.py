from django.db import models
from apps.users.models import User
from apps.orders.models import Order


class Notification(models.Model):
    """
    In-app notification system.
    """
    
    class NotificationType(models.TextChoices):
        ORDER = 'ORDER', 'Order Notification'
        PAYMENT = 'PAYMENT', 'Payment Notification'
        SYSTEM = 'SYSTEM', 'System Notification'
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    
    is_read = models.BooleanField(default=False, db_index=True)
    
    related_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"
