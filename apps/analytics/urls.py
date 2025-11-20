from django.urls import path
from .views import (
    delivery_summary_view,
    rider_performance_view,
    financials_view,
    trends_view,
)

app_name = 'analytics'

urlpatterns = [
    path('delivery-summary/', delivery_summary_view, name='delivery-summary'),
    path('rider-performance/', rider_performance_view, name='rider-performance'),
    path('financials/', financials_view, name='financials'),
    path('trends/', trends_view, name='trends'),
]
