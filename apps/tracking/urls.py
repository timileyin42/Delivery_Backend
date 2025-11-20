from django.urls import path
from .views import (
    update_location_view,
    order_location_view,
    all_riders_locations_view,
    rider_location_history_view,
)

app_name = 'tracking'

urlpatterns = [
    path('location/', update_location_view, name='update-location'),
    path('orders/<int:order_id>/location/', order_location_view, name='order-location'),
    path('riders/locations/', all_riders_locations_view, name='all-riders-locations'),
    path('riders/<int:rider_id>/history/', rider_location_history_view, name='rider-location-history'),
]
