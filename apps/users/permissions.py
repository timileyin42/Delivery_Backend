from rest_framework import permissions
from .models import User


class IsAdmin(permissions.BasePermission):
    """
    Permission class for Admin users only.
    """
    message = "Only administrators can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.ADMIN
        )


class IsManager(permissions.BasePermission):
    """
    Permission class for Manager users only.
    """
    message = "Only managers can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.MANAGER
        )


class IsRider(permissions.BasePermission):
    """
    Permission class for Rider users only.
    """
    message = "Only riders can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == User.Role.RIDER
        )


class IsAdminOrManager(permissions.BasePermission):
    """
    Permission class for Admin or Manager users.
    """
    message = "Only administrators or managers can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in [User.Role.ADMIN, User.Role.MANAGER]
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class for object owner or Admin.
    """
    message = "You can only access your own resources."
    
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.role == User.Role.ADMIN:
            return True
        
        # Check if obj has a 'user' attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Otherwise check if obj is the user itself
        return obj == request.user
