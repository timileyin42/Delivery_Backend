from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import RiderProfile
from apps.orders.models import Order
from .location_serializers import (
    RiderLocationUpdateSerializer,
    OrderTrackingSerializer,
    AdminRiderLocationSerializer
)
from .location_permissions import (
    CanUpdateRiderLocation,
    CanViewRiderLocation,
    CanTrackOrder
)
from apps.common.utils import success_response, error_response


@extend_schema(
    tags=['Location Tracking'],
    summary='Update rider location',
    description='Riders can update their current GPS location for real-time tracking',
    request=RiderLocationUpdateSerializer,
    responses={
        200: OpenApiResponse(description='Location updated successfully'),
        400: OpenApiResponse(description='Invalid coordinates'),
        403: OpenApiResponse(description='Permission denied')
    }
)
@api_view(['POST'])
@permission_classes([CanUpdateRiderLocation])
def update_rider_location(request):
    """
    Update rider's current location.
    POST /api/riders/location/update/
    """
    try:
        rider_profile = request.user.rider_profile
    except RiderProfile.DoesNotExist:
        return Response(
            error_response("Rider profile not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = RiderLocationUpdateSerializer(data=request.data)
    if serializer.is_valid():
        rider_profile = serializer.update_location(rider_profile)
        
        return Response(
            success_response(
                message="Location updated successfully",
                data={
                    'latitude': float(rider_profile.current_location_lat),
                    'longitude': float(rider_profile.current_location_lng),
                    'updated_at': rider_profile.last_location_update.isoformat()
                }
            ),
            status=status.HTTP_200_OK
        )
    
    return Response(
        error_response(
            message="Invalid location data",
            errors=serializer.errors
        ),
        status=status.HTTP_400_BAD_REQUEST
    )


@extend_schema(
    tags=['Location Tracking'],
    summary='Track order with rider location',
    description='Get real-time order tracking information including rider location and ETA',
    parameters=[
        OpenApiParameter(
            name='order_number',
            type=str,
            location=OpenApiParameter.PATH,
            description='Order number to track'
        )
    ],
    responses={
        200: OrderTrackingSerializer,
        404: OpenApiResponse(description='Order not found'),
        403: OpenApiResponse(description='Permission denied')
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def track_order(request, order_number):
    """
    Track order with real-time rider location.
    GET /api/orders/<order_number>/track/
    """
    try:
        order = Order.objects.select_related('rider__user', 'customer').get(
            order_number=order_number
        )
    except Order.DoesNotExist:
        return Response(
            error_response("Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check permission
    permission = CanTrackOrder()
    if not permission.has_object_permission(request, None, order):
        return Response(
            error_response("You don't have permission to track this order"),
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrderTrackingSerializer(order)
    
    return Response(
        success_response(
            message="Order tracking information retrieved successfully",
            data=serializer.data
        ),
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=['Location Tracking'],
    summary='Get rider location (Admin)',
    description='Admin/Manager can view any rider\'s current location',
    parameters=[
        OpenApiParameter(
            name='rider_id',
            type=int,
            location=OpenApiParameter.PATH,
            description='Rider profile ID'
        )
    ],
    responses={
        200: AdminRiderLocationSerializer,
        404: OpenApiResponse(description='Rider not found'),
        403: OpenApiResponse(description='Permission denied - Admin only')
    }
)
@api_view(['GET'])
@permission_classes([CanViewRiderLocation])
def get_rider_location(request, rider_id):
    """
    Get specific rider's location (Admin/Manager only).
    GET /api/riders/<rider_id>/location/
    """
    try:
        rider = RiderProfile.objects.select_related('user').get(id=rider_id)
    except RiderProfile.DoesNotExist:
        return Response(
            error_response("Rider not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check object-level permission
    permission = CanViewRiderLocation()
    if not permission.has_object_permission(request, None, rider):
        return Response(
            error_response("You don't have permission to view this rider's location"),
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AdminRiderLocationSerializer(rider)
    
    return Response(
        success_response(
            message="Rider location retrieved successfully",
            data=serializer.data
        ),
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=['Location Tracking'],
    summary='Get all active riders locations (Admin)',
    description='Get current location of all active riders for fleet management',
    responses={
        200: AdminRiderLocationSerializer(many=True),
        403: OpenApiResponse(description='Permission denied - Admin only')
    }
)
@api_view(['GET'])
@permission_classes([CanViewRiderLocation])
def get_all_riders_locations(request):
    """
    Get all active riders' locations (Admin/Manager only).
    GET /api/riders/locations/all/
    """
    # Filter only active and available riders
    riders = RiderProfile.objects.filter(
        status='ACTIVE',
        is_available=True
    ).select_related('user')
    
    serializer = AdminRiderLocationSerializer(riders, many=True)
    
    return Response(
        success_response(
            message=f"Retrieved {riders.count()} active rider locations",
            data=serializer.data
        ),
        status=status.HTTP_200_OK
    )
