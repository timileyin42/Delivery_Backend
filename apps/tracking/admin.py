from django.contrib import admin
from .models import RiderLocation


@admin.register(RiderLocation)
class RiderLocationAdmin(admin.ModelAdmin):
    """
    Admin interface for RiderLocation model.
    """
    list_display = ['rider', 'latitude', 'longitude', 'order', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['rider__email', 'rider__first_name', 'rider__last_name']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
