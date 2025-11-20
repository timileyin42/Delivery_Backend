from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusLog


@receiver(post_save, sender=Order)
def create_status_log(sender, instance, created, **kwargs):
    """
    Create status log entry when order is created or status changes.
    """
    if created:
        OrderStatusLog.objects.create(
            order=instance,
            status=instance.status,
            changed_by=instance.created_by,
            notes="Order created"
        )


@receiver(pre_save, sender=Order)
def track_status_change(sender, instance, **kwargs):
    """
    Track status changes and update timestamps.
    """
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            
            # If status changed, create log entry
            if old_instance.status != instance.status:
                # Update timestamps based on new status
                if instance.status == Order.Status.ASSIGNED and not instance.assigned_at:
                    instance.assigned_at = timezone.now()
                elif instance.status == Order.Status.PICKED and not instance.picked_at:
                    instance.picked_at = timezone.now()
                elif instance.status == Order.Status.DELIVERED and not instance.delivered_at:
                    instance.delivered_at = timezone.now()
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Order)
def update_rider_earnings(sender, instance, created, **kwargs):
    """
    Update rider earnings when order is delivered.
    """
    if not created and instance.status == Order.Status.DELIVERED:
        if instance.assigned_rider and hasattr(instance.assigned_rider, 'rider_profile'):
            from apps.riders.models import RiderEarnings
            from apps.common.utils import calculate_rider_earnings
            
            # Check if earnings already recorded
            if not RiderEarnings.objects.filter(order=instance).exists():
                rider_amount = calculate_rider_earnings(float(instance.delivery_fee))
                
                # Create earnings record
                RiderEarnings.objects.create(
                    rider=instance.assigned_rider.rider_profile,
                    order=instance,
                    amount=rider_amount,
                    delivery_fee=instance.delivery_fee
                )
                
                # Update rider stats and earnings
                instance.assigned_rider.rider_profile.update_stats(delivery_successful=True)
                instance.assigned_rider.rider_profile.add_earnings(rider_amount)


@receiver(post_save, sender=Order)
def update_failed_delivery_stats(sender, instance, created, **kwargs):
    """
    Update rider stats for failed deliveries.
    """
    if not created and instance.status == Order.Status.FAILED:
        if instance.assigned_rider and hasattr(instance.assigned_rider, 'rider_profile'):
            instance.assigned_rider.rider_profile.update_stats(delivery_successful=False)


@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Send notifications on order events.
    """
    from apps.notifications.models import Notification
    
    if created:
        # Notify admins of new order
        from apps.users.models import User
        admins = User.objects.filter(role=User.Role.ADMIN)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                title="New Order Created",
                message=f"Order {instance.order_number} has been created.",
                related_order=instance
            )
    
    # Notify rider when assigned
    if instance.assigned_rider and instance.status == Order.Status.ASSIGNED:
        Notification.objects.create(
            recipient=instance.assigned_rider,
            title="New Delivery Assignment",
            message=f"You have been assigned order {instance.order_number}.",
            related_order=instance
        )
