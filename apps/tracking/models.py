from django.db import models
from apps.users.models import User
from apps.orders.models import Order


class RiderLocation(models.Model):
    """
    Track rider GPS locations in real-time.
    """
    rider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='locations',
        limit_choices_to={'role': 'RIDER'}
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_locations'
    )
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.FloatField(
        null=True,
        blank=True,
        help_text="Accuracy in meters"
    )
    speed = models.FloatField(
        null=True,
        blank=True,
        help_text="Speed in km/h"
    )
    heading = models.FloatField(
        null=True,
        blank=True,
        help_text="Direction in degrees"
    )
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'rider_locations'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['rider', '-timestamp']),
            models.Index(fields=['order', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.rider.get_full_name()} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update rider profile with current location
        if hasattr(self.rider, 'rider_profile'):
            self.rider.rider_profile.current_location_lat = self.latitude
            self.rider.rider_profile.current_location_lng = self.longitude
            self.rider.rider_profile.save(update_fields=[
                'current_location_lat', 'current_location_lng'
            ])
