from django.urls import path
from .views import (
    OrderListView,
    OrderCreateView,
    OrderDetailView,
    assign_order_view,
    reassign_order_view,
    cancel_order_view,
    update_order_status_view,
)
from .gcs_views import (
    get_delivery_proof_upload_url_view,
    confirm_delivery_proof_upload_view,
    get_delivery_proof_url_view,
)
from apps.riders.location_views import track_order

app_name = 'orders'

urlpatterns = [
    # Main Order Operations
    path('', OrderListView.as_view(), name='order-list'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    
    # Order Actions
    path('<int:pk>/assign/', assign_order_view, name='order-assign'),
    path('<int:pk>/reassign/', reassign_order_view, name='order-reassign'),
    path('<int:pk>/cancel/', cancel_order_view, name='order-cancel'),
    path('<int:pk>/status/', update_order_status_view, name='order-status-update'),
    
    # Order Tracking
    path('<str:order_number>/track/', track_order, name='order-track'),
    
    # Delivery Proof (GCS)
    path('<int:order_id>/upload-proof-url/', get_delivery_proof_upload_url_view, name='upload-proof-url'),
    path('<int:order_id>/confirm-proof/', confirm_delivery_proof_upload_view, name='confirm-proof'),
    path('<int:order_id>/delivery-proof/', get_delivery_proof_url_view, name='delivery-proof'),
]
