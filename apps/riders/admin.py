from django.contrib import admin
from .models import RiderProfile, RiderEarnings


@admin.register(RiderProfile)
class RiderProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for RiderProfile model.
    """
    list_display = [
        'user', 'vehicle_type', 'status', 'rating', 'total_deliveries',
        'success_rate', 'total_earnings', 'is_available', 'created_at'
    ]
    list_filter = ['status', 'vehicle_type', 'is_available', 'documents_verified']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'vehicle_plate_number']
    ordering = ['-created_at']
    readonly_fields = [
        'total_deliveries', 'successful_deliveries', 'failed_deliveries',
        'success_rate', 'total_earnings', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_model', 'vehicle_plate_number', 'license_number')
        }),
        ('Status', {
            'fields': ('status', 'is_available', 'onboarding_completed', 'documents_verified')
        }),
        ('Performance', {
            'fields': (
                'rating', 'total_deliveries', 'successful_deliveries',
                'failed_deliveries', 'success_rate', 'total_earnings'
            )
        }),
        ('Location', {
            'fields': ('current_location_lat', 'current_location_lng')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(RiderEarnings)
class RiderEarningsAdmin(admin.ModelAdmin):
    """
    Admin interface for RiderEarnings model.
    """
    list_display = ['rider', 'order', 'amount', 'delivery_fee', 'earned_at']
    list_filter = ['earned_at']
    search_fields = ['rider__user__email', 'order__order_number']
    ordering = ['-earned_at']
    readonly_fields = ['earned_at']
