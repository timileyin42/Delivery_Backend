from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User


class RiderProfile(models.Model):
    """
    Extended profile for Rider users.
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'
    
    class VehicleType(models.TextChoices):
        MOTORCYCLE = 'MOTORCYCLE', 'Motorcycle'
        BICYCLE = 'BICYCLE', 'Bicycle'
        CAR = 'CAR', 'Car'
        VAN = 'VAN', 'Van'
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='rider_profile'
    )
    
    # Vehicle Information
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.MOTORCYCLE
    )
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_plate_number = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    
    # Status and Performance
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=5.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    total_deliveries = models.IntegerField(default=0)
    successful_deliveries = models.IntegerField(default=0)
    failed_deliveries = models.IntegerField(default=0)
    
    # Earnings
    total_earnings = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    
    # Availability
    is_available = models.BooleanField(default=True)
    current_location_lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    current_location_lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    onboarding_completed = models.BooleanField(default=False)
    documents_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rider_profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.vehicle_type}"
    
    @property
    def success_rate(self):
        """Calculate delivery success rate."""
        if self.total_deliveries == 0:
            return 0.0
        return round((self.successful_deliveries / self.total_deliveries) * 100, 2)
    
    @property
    def is_location_fresh(self):
        """Check if location data is recent (within last 5 minutes)."""
        if not self.last_location_update:
            return False
        from django.utils import timezone
        from datetime import timedelta
        max_age = timedelta(minutes=5)
        return timezone.now() - self.last_location_update < max_age
    
    def update_stats(self, delivery_successful=True):
        """Update rider statistics after delivery."""
        self.total_deliveries += 1
        if delivery_successful:
            self.successful_deliveries += 1
        else:
            self.failed_deliveries += 1
        self.save(update_fields=[
            'total_deliveries',
            'successful_deliveries',
            'failed_deliveries'
        ])
    
    def add_earnings(self, amount):
        """Add earnings to rider's total."""
        self.total_earnings += amount
        self.save(update_fields=['total_earnings'])


class RiderEarnings(models.Model):
    """
    Track individual earnings per delivery.
    """
    rider = models.ForeignKey(
        RiderProfile,
        on_delete=models.CASCADE,
        related_name='earnings_history'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='rider_earning'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rider_earnings'
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['rider', 'earned_at']),
        ]
    
    def __str__(self):
        return f"{self.rider.user.get_full_name()} - ₦{self.amount}"
