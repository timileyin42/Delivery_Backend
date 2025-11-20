from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def create_rider_profile(sender, instance, created, **kwargs):
    """
    Create rider profile when a user with RIDER role is created.
    """
    if created and instance.role == User.Role.RIDER:
        from apps.riders.models import RiderProfile
        RiderProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """
    Log user creation for audit trail.
    """
    if created:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"New user created: {instance.email} ({instance.role})")
