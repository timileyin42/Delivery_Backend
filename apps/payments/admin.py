from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model.
    """
    list_display = [
        'reference', 'order', 'amount', 'status',
        'payment_method', 'created_at', 'paid_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['reference', 'paystack_reference', 'order__order_number']
    ordering = ['-created_at']
    readonly_fields = ['reference', 'created_at', 'updated_at', 'paid_at']
