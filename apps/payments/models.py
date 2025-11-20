from django.db import models
from apps.orders.models import Order
from apps.common.utils import generate_transaction_reference


class Transaction(models.Model):
    """
    Payment transaction records.
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        ABANDONED = 'ABANDONED', 'Abandoned'
    
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    payment_method = models.CharField(max_length=50, blank=True)
    paystack_reference = models.CharField(max_length=200, blank=True)
    authorization_url = models.URLField(blank=True)
    access_code = models.CharField(max_length=200, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['paystack_reference']),
        ]
    
    def __str__(self):
        return f"{self.reference} - ₦{self.amount} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_transaction_reference()
        super().save(*args, **kwargs)
