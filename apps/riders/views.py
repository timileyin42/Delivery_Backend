from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum from datetime import datetime, timedelta
from django.utils import timezone

from .models import RiderProfile, RiderEarnings
from .serializers import (
    RiderProfileSerializer,
    RiderProfileUpdateSerializer,
    RiderPerformanceSerializer,
    RiderEarningsSerializer
)
from apps.users.permissions import IsAdmin, IsAdminOrManager, IsRider
from apps.common.utils import success_response, error_response
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer


class RiderListView(generics.ListAPIView):
    """
    List all riders (Admin/Manager).
    GET /api/riders/
    """
    serializer_class = RiderProfileSerializer
    permission_classes = [IsAdminOrManager]
    queryset = RiderProfile.objects.select_related('user').all()
    filterset_fields = ['status', 'is_available', 'vehicle_type']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'vehicle_plate_number']
    ordering_fields = ['created_at', 'rating', 'total_deliveries']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success_response(
                data=serializer.data,
                message="Riders retrieved successfully"
            )
        )


class RiderDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update rider details.
    GET/PATCH /api/riders/{id}/
    """
    serializer_class = RiderProfileSerializer
    permission_classes = [IsAdminOrManager]
    queryset = RiderProfile.objects.select_related('user').all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(
            success_response(
                data=serializer.data,
                message="Rider details retrieved successfully"
            )
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            success_response(
                data=serializer.data,
                message="Rider details updated successfully"
            )
        )


@api_view(['GET'])
@permission_classes([IsRider])
def rider_tasks_view(request):
    """
    Get rider's assigned tasks (orders).
    GET /api/riders/tasks/
    """
    try:
        rider_profile = request.user.rider_profile
    except RiderProfile.DoesNotExist:
        return Response(
            error_response(message="Rider profile not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get orders assigned to this rider
    status_filter = request.query_params.get('status', None)
    
    orders = Order.objects.filter(assigned_rider=request.user)
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Order by status priority and created date
    orders = orders.order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    
    return Response(
        success_response(
            data=serializer.data,
            message="Tasks retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsRider])
def rider_earnings_view(request):
    """
    Get rider's earnings with filters.
    GET /api/riders/earnings/?period=week|month|all
    """
    try:
        rider_profile = request.user.rider_profile
    except RiderProfile.DoesNotExist:
        return Response(
            error_response(message="Rider profile not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get period filter
    period = request.query_params.get('period', 'all')
    
    earnings_query = RiderEarnings.objects.filter(rider=rider_profile)
    
    now = timezone.now()
    
    if period == 'week':
        start_date = now - timedelta(days=7)
        earnings_query = earnings_query.filter(earned_at__gte=start_date)
    elif period == 'month':
        start_date = now - timedelta(days=30)
        earnings_query = earnings_query.filter(earned_at__gte=start_date)
    elif period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        earnings_query = earnings_query.filter(earned_at__gte=start_date)
    
    earnings = earnings_query.order_by('-earned_at')
    
    # Calculate total
    total_amount = earnings.aggregate(total=Sum('amount'))['total'] or 0
    
    serializer = RiderEarningsSerializer(earnings, many=True)
    
    return Response(
        success_response(
            data={
                'earnings': serializer.data,
                'total': float(total_amount),
                'count': earnings.count(),
                'period': period
            },
            message="Earnings retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsRider])
def rider_performance_view(request):
    """
    Get rider's performance metrics.
    GET /api/riders/performance/
    """
    try:
        rider_profile = request.user.rider_profile
    except RiderProfile.DoesNotExist:
        return Response(
            error_response(message="Rider profile not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Weekly stats
    weekly_earnings = RiderEarnings.objects.filter(
        rider=rider_profile,
        earned_at__gte=week_ago
    )
    deliveries_this_week = weekly_earnings.count()
    earnings_this_week = weekly_earnings.aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly stats
    monthly_earnings = RiderEarnings.objects.filter(
        rider=rider_profile,
        earned_at__gte=month_ago
    )
    deliveries_this_month = monthly_earnings.count()
    earnings_this_month = monthly_earnings.aggregate(total=Sum('amount'))['total'] or 0
    
    performance_data = {
        'total_deliveries': rider_profile.total_deliveries,
        'successful_deliveries': rider_profile.successful_deliveries,
        'failed_deliveries': rider_profile.failed_deliveries,
        'success_rate': rider_profile.success_rate,
        'total_earnings': rider_profile.total_earnings,
        'average_rating': rider_profile.rating,
        'deliveries_this_week': deliveries_this_week,
        'earnings_this_week': earnings_this_week,
        'deliveries_this_month': deliveries_this_month,
        'earnings_this_month': earnings_this_month
    }
    
    serializer = RiderPerformanceSerializer(data=performance_data)
    serializer.is_valid(raise_exception=True)
    
    return Response(
        success_response(
            data=serializer.data,
            message="Performance metrics retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['PATCH'])
@permission_classes([IsRider])
def rider_profile_update_view(request):
    """
    Update rider's own profile.
    PATCH /api/riders/profile/
    """
    try:
        rider_profile = request.user.rider_profile
    except RiderProfile.DoesNotExist:
        return Response(
            error_response(message="Rider profile not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = RiderProfileUpdateSerializer(
        rider_profile,
        data=request.data,
        partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response(
        success_response(
            data=RiderProfileSerializer(rider_profile).data,
            message="Profile updated successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def available_riders_view(request):
    """
    Get all available riders for assignment.
    GET /api/riders/available/
    """
    riders = RiderProfile.objects.filter(
        status=RiderProfile.Status.ACTIVE,
        is_available=True
    ).select_related('user')
    
    serializer = RiderProfileSerializer(riders, many=True)
    
    return Response(
        success_response(
            data=serializer.data,
            message="Available riders retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )
