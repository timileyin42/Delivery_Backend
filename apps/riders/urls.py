from django.urls import path
from .views import (
    RiderListView,
    RiderDetailView,
    rider_tasks_view,
    rider_earnings_view,
    rider_performance_view,
    rider_profile_update_view,
    available_riders_view,
)
from .location_views import (
    update_rider_location,
    get_rider_location,
    get_all_riders_locations,
)

app_name = 'riders'

urlpatterns = [
    # Rider Management (Admin/Manager)
    path('', RiderListView.as_view(), name='rider-list'),
    path('<int:pk>/', RiderDetailView.as_view(), name='rider-detail'),
    path('available/', available_riders_view, name='available-riders'),
    
    # Rider Self-Service
    path('tasks/', rider_tasks_view, name='rider-tasks'),
    path('earnings/', rider_earnings_view, name='rider-earnings'),
    path('performance/', rider_performance_view, name='rider-performance'),
    path('profile/', rider_profile_update_view, name='rider-profile-update'),
    
    # Location Tracking
    path('location/update/', update_rider_location, name='update-location'),
    path('<int:rider_id>/location/', get_rider_location, name='rider-location'),
    path('locations/all/', get_all_riders_locations, name='all-riders-locations'),
]
