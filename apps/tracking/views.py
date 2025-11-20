from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .models import RiderLocation
from .serializers import LocationUpdateSerializer, LocationSerializer
from apps.users.permissions import IsRider, IsAdminOrManager
from apps.common.utils import success_response, error_response
from apps.orders.models import Order


@api_view(['POST'])
@permission_classes([IsRider])
def update_location_view(request):
    """
    Rider submits current location.
    POST /api/tracking/location/
    """
    serializer = LocationUpdateSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    location = serializer.save()
    
    return Response(
        success_response(
            data=LocationSerializer(location).data,
            message="Location updated successfully"
        ),
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_location_view(request, order_id):
    """
    Get current location of order's assigned rider.
    GET /api/tracking/orders/{id}/location/
    """
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not order.assigned_rider:
        return Response(
            error_response(message="No rider assigned to this order"),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get latest location
    latest_location = RiderLocation.objects.filter(
        rider=order.assigned_rider
    ).order_by('-timestamp').first()
    
    if not latest_location:
        return Response(
            error_response(message="No location data available"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(
        success_response(
            data=LocationSerializer(latest_location).data,
            message="Location retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def all_riders_locations_view(request):
    """
    Get current locations of all active riders.
    GET /api/tracking/riders/locations/
    """
    from apps.riders.models import RiderProfile
    
    # Get active riders
    active_riders = RiderProfile.objects.filter(
        status='ACTIVE',
        is_available=True
    ).select_related('user')
    
    locations_data = []
    
    for rider_profile in active_riders:
        latest_location = RiderLocation.objects.filter(
            rider=rider_profile.user
        ).order_by('-timestamp').first()
        
        if latest_location:
            locations_data.append({
                'rider_id': rider_profile.user.id,
                'rider_name': rider_profile.user.get_full_name(),
                'latitude': float(latest_location.latitude),
                'longitude': float(latest_location.longitude),
                'last_updated': latest_location.timestamp,
                'is_on_delivery': RiderLocation.objects.filter(
                    rider=rider_profile.user,
                    order__isnull=False,
                    timestamp__gte=timezone.now() - timedelta(minutes=30)
                ).exists()
            })
    
    return Response(
        success_response(
            data=locations_data,
            message="Rider locations retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def rider_location_history_view(request, rider_id):
    """
    Get location history for a specific rider.
    GET /api/tracking/riders/{id}/history/
    """
    from apps.users.models import User
    
    try:
        rider = User.objects.get(pk=rider_id, role=User.Role.RIDER)
    except User.DoesNotExist:
        return Response(
            error_response(message="Rider not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get date filter
    hours = int(request.query_params.get('hours', 24))
    start_time = timezone.now() - timedelta(hours=hours)
    
    locations = RiderLocation.objects.filter(
        rider=rider,
        timestamp__gte=start_time
    ).order_by('-timestamp')
    
    serializer = LocationSerializer(locations, many=True)
    
    return Response(
        success_response(
            data=serializer.data,
            message=f"Location history for last {hours} hours retrieved"
        ),
        status=status.HTTP_200_OK
    )
