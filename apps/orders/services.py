from django.db import transaction
from django.utils import timezone
from .models import Order, OrderStatusLog
from apps.users.models import User
from apps.common.exceptions import ValidationException, NotFoundException


class OrderService:
    """
    Business logic for order operations.
    """
    
    @staticmethod
    def assign_order_to_rider(order, rider_id, assigned_by):
        """
        Assign order to a rider with validation.
        """
        if not order.can_be_assigned:
            raise ValidationException(
                f"Order {order.order_number} cannot be assigned. Current status: {order.status}"
            )
        
        try:
            rider = User.objects.get(id=rider_id, role=User.Role.RIDER)
        except User.DoesNotExist:
            raise NotFoundException("Rider not found")
        
        if not hasattr(rider, 'rider_profile'):
            raise ValidationException("User is not a valid rider")
        
        rider_profile = rider.rider_profile
        
        if rider_profile.status != 'ACTIVE':
            raise ValidationException(f"Rider is not active. Status: {rider_profile.status}")
        
        if not rider_profile.is_available:
            raise ValidationException("Rider is not available for assignment")
        
        # Assign the order
        with transaction.atomic():
            order.assigned_rider = rider
            order.status = Order.Status.ASSIGNED
            order.assigned_at = timezone.now()
            order.save()
            
            # Create status log
            OrderStatusLog.objects.create(
                order=order,
                status=Order.Status.ASSIGNED,
                changed_by=assigned_by,
                notes=f"Assigned to {rider.get_full_name()}"
            )
        
        return order
    
    @staticmethod
    def reassign_order(order, new_rider_id, reassigned_by):
        """
        Reassign order to a different rider.
        """
        if order.status in [Order.Status.DELIVERED, Order.Status.FAILED, Order.Status.CANCELLED]:
            raise ValidationException(
                f"Cannot reassign order with status: {order.status}"
            )
        
        try:
            new_rider = User.objects.get(id=new_rider_id, role=User.Role.RIDER)
        except User.DoesNotExist:
            raise NotFoundException("Rider not found")
        
        if not hasattr(new_rider, 'rider_profile'):
            raise ValidationException("User is not a valid rider")
        
        new_rider_profile = new_rider.rider_profile
        
        if new_rider_profile.status != 'ACTIVE':
            raise ValidationException("New rider is not active")
        
        if not new_rider_profile.is_available:
            raise ValidationException("New rider is not available")
        
        old_rider = order.assigned_rider
        
        with transaction.atomic():
            order.assigned_rider = new_rider
            order.status = Order.Status.ASSIGNED
            order.assigned_at = timezone.now()
            order.save()
            
            OrderStatusLog.objects.create(
                order=order,
                status=Order.Status.ASSIGNED,
                changed_by=reassigned_by,
                notes=f"Reassigned from {old_rider.get_full_name() if old_rider else 'Unassigned'} to {new_rider.get_full_name()}"
            )
        
        return order
    
    @staticmethod
    def cancel_order(order, cancelled_by, reason=""):
        """
        Cancel an order.
        """
        if not order.can_be_cancelled:
            raise ValidationException(
                f"Order {order.order_number} cannot be cancelled. Current status: {order.status}"
            )
        
        with transaction.atomic():
            order.status = Order.Status.CANCELLED
            order.save()
            
            OrderStatusLog.objects.create(
                order=order,
                status=Order.Status.CANCELLED,
                changed_by=cancelled_by,
                notes=f"Order cancelled. Reason: {reason}" if reason else "Order cancelled"
            )
        
        return order
    
    @staticmethod
    def update_order_status(order, new_status, updated_by, notes="", delivery_proof=None):
        """
        Update order status with validation.
        """
        with transaction.atomic():
            order.status = new_status
            
            if delivery_proof:
                order.delivery_proof_image = delivery_proof
            
            if notes:
                order.delivery_notes = notes
            
            order.save()
            
            OrderStatusLog.objects.create(
                order=order,
                status=new_status,
                changed_by=updated_by,
                notes=notes or f"Status updated to {new_status}"
            )
        
        return order
