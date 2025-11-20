from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.validators import validate_nigerian_phone


class User(AbstractUser):
    """
    Custom User model with role-based access.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        RIDER = 'RIDER', 'Rider'
    
    # Override username to use email
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    # Profile fields
    phone = models.CharField(
        max_length=20,
        validators=[validate_nigerian_phone],
        help_text="Phone number in Nigerian format"
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.RIDER,
        db_index=True
    )
    
    # Metadata
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)  # Email verification status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Set email as the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
    
    @property
    def is_admin(self):
        """Check if user is admin."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_manager(self):
        """Check if user is manager."""
        return self.role == self.Role.MANAGER
    
    @property
    def is_rider(self):
        """Check if user is rider."""
        return self.role == self.Role.RIDER
    
    def save(self, *args, **kwargs):
        # Generate username from email if not provided
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
