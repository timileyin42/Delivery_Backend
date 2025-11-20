from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.orders.models import Order
from apps.riders.models import RiderProfile, RiderEarnings
from apps.payments.models import Transaction


class AnalyticsService:
    """
    Service for generating analytics and reports.
    """
    
    @staticmethod
    def get_delivery_summary(start_date=None, end_date=None):
        """
        Get delivery statistics for a date range.
        """
        queryset = Order.objects.all()
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        total_orders = queryset.count()
        
        stats = {
            'total_orders': total_orders,
            'delivered': queryset.filter(status=Order.Status.DELIVERED).count(),
            'in_progress': queryset.filter(
                status__in=[
                    Order.Status.CREATED,
                    Order.Status.ASSIGNED,
                    Order.Status.ACCEPTED,
                    Order.Status.PICKED,
                    Order.Status.IN_TRANSIT
                ]
            ).count(),
            'failed': queryset.filter(status=Order.Status.FAILED).count(),
            'cancelled': queryset.filter(status=Order.Status.CANCELLED).count(),
            'total_revenue': queryset.aggregate(total=Sum('delivery_fee'))['total'] or 0,
            'average_delivery_fee': queryset.aggregate(avg=Avg('delivery_fee'))['avg'] or 0,
        }
        
        # Success rate
        if stats['delivered'] + stats['failed'] > 0:
            stats['success_rate'] = round(
                (stats['delivered'] / (stats['delivered'] + stats['failed'])) * 100,
                2
            )
        else:
            stats['success_rate'] = 0
        
        return stats
    
    @staticmethod
    def get_rider_performance_summary():
        """
        Get overall rider performance metrics.
        """
        riders = RiderProfile.objects.filter(status='ACTIVE')
        
        return {
            'total_active_riders': riders.count(),
            'available_riders': riders.filter(is_available=True).count(),
            'total_deliveries': riders.aggregate(total=Sum('total_deliveries'))['total'] or 0,
            'successful_deliveries': riders.aggregate(total=Sum('successful_deliveries'))['total'] or 0,
            'average_rating': riders.aggregate(avg=Avg('rating'))['avg'] or 0,
            'total_earnings': riders.aggregate(total=Sum('total_earnings'))['total'] or 0,
        }
    
    @staticmethod
    def get_financial_summary(start_date=None, end_date=None):
        """
        Get financial metrics.
        """
        transactions = Transaction.objects.filter(status=Transaction.Status.SUCCESS)
        
        if start_date:
            transactions = transactions.filter(created_at__gte=start_date)
        if end_date:
            transactions = transactions.filter(created_at__lte=end_date)
        
        earnings = RiderEarnings.objects.all()
        
        if start_date:
            earnings = earnings.filter(earned_at__gte=start_date)
        if end_date:
            earnings = earnings.filter(earned_at__lte=end_date)
        
        total_collected = transactions.aggregate(total=Sum('amount'))['total'] or 0
        total_rider_earnings = earnings.aggregate(total=Sum('amount'))['total'] or 0
        company_revenue = float(total_collected) - float(total_rider_earnings)
        
        return {
            'total_collected': total_collected,
            'total_rider_earnings': total_rider_earnings,
            'company_revenue': company_revenue,
            'successful_transactions': transactions.count(),
            'average_transaction_value': transactions.aggregate(avg=Avg('amount'))['avg'] or 0,
        }
    
    @staticmethod
    def get_trends(days=30):
        """
        Get trend data for specified number of days.
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Group orders by day
        from django.db.models.functions import TruncDate
        
        daily_orders = Order.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Peak hours analysis
        from django.db.models.functions import ExtractHour
        
        hourly_distribution = Order.objects.filter(
            created_at__gte=start_date
        ).annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        return {
            'daily_orders': list(daily_orders),
            'peak_hours': list(hourly_distribution),
            'period_days': days
        }
