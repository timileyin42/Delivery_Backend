from rest_framework import permissions
from apps.orders.models import Order


class CanUpdateRiderLocation(permissions.BasePermission):
    """
    Permission to update rider location.
    Only the rider can update their own location.
    """
    message = "Only riders can update their own location."

    def has_permission(self, request, view):
        # User must be authenticated
        if not request.user.is_authenticated:
            return False
        
        # User must be a rider
        if request.user.role != 'RIDER':
            return False
        
        # User must have a rider profile
        return hasattr(request.user, 'rider_profile')


class CanViewRiderLocation(permissions.BasePermission):
    """
    Permission to view rider location.
    Order customer, admin, manager, or the rider themselves can view.
    """
    message = "You don't have permission to view this rider's location."

    def has_permission(self, request, view):
        # User must be authenticated
        if not request.user.is_authenticated:
            return False
        
        # Admin and managers can view any location
        if request.user.role in ['ADMIN', 'MANAGER']:
            return True
        
        # Let object-level permission handle rider/customer checks
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for rider location.
        obj is a RiderProfile instance.
        """
        user = request.user
        
        # Admin and managers have full access
        if user.role in ['ADMIN', 'MANAGER']:
            return True
        
        # Rider viewing their own location
        if user.role == 'RIDER' and hasattr(user, 'rider_profile'):
            return user.rider_profile.id == obj.id
        
        # Customer can only view if they have an active order with this rider
        active_order = Order.objects.filter(
            customer=user,
            rider=obj,
            status__in=['ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']
        ).exists()
        
        return active_order


class CanTrackOrder(permissions.BasePermission):
    """
    Permission to track an order.
    Only the customer who created the order, admin, manager, or assigned rider.
    """
    message = "You don't have permission to track this order."

    def has_permission(self, request, view):
        # User must be authenticated
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for order tracking.
        obj is an Order instance.
        """
        user = request.user
        
        # Admin and managers can track any order
        if user.role in ['ADMIN', 'MANAGER']:
            return True
        
        # Customer can track their own order
        if obj.customer == user:
            return True
        
        # Assigned rider can track the order
        if obj.rider and user.role == 'RIDER':
            if hasattr(user, 'rider_profile') and obj.rider.id == user.rider_profile.id:
                return True
        
        return False
