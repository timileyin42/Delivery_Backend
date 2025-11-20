from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .services import AnalyticsService
from apps.users.permissions import IsAdminOrManager
from apps.common.utils import success_response


@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def delivery_summary_view(request):
    """
    Get delivery summary statistics.
    GET /api/analytics/delivery-summary/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        start_date = timezone.datetime.fromisoformat(start_date)
    if end_date:
        end_date = timezone.datetime.fromisoformat(end_date)
    
    data = AnalyticsService.get_delivery_summary(start_date, end_date)
    
    return Response(
        success_response(
            data=data,
            message="Delivery summary retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def rider_performance_view(request):
    """
    Get rider performance metrics.
    GET /api/analytics/rider-performance/
    """
    data = AnalyticsService.get_rider_performance_summary()
    
    return Response(
        success_response(
            data=data,
            message="Rider performance metrics retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def financials_view(request):
    """
    Get financial analytics.
    GET /api/analytics/financials/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    """
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if start_date:
        start_date = timezone.datetime.fromisoformat(start_date)
    if end_date:
        end_date = timezone.datetime.fromisoformat(end_date)
    
    data = AnalyticsService.get_financial_summary(start_date, end_date)
    
    return Response(
        success_response(
            data=data,
            message="Financial metrics retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsAdminOrManager])
def trends_view(request):
    """
    Get trend analysis.
    GET /api/analytics/trends/?days=30
    """
    days = int(request.query_params.get('days', 30))
    
    data = AnalyticsService.get_trends(days)
    
    return Response(
        success_response(
            data=data,
            message="Trends retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )
