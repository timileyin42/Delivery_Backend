from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Order, OrderStatusLog
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderAssignmentSerializer,
    OrderStatusUpdateSerializer
)
from .services import OrderService
from apps.users.permissions import IsAdminOrManager, IsRider
from apps.common.utils import success_response, error_response


class OrderListView(generics.ListAPIView):
    """
    List all orders with filtering.
    GET /api/orders/
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.select_related('assigned_rider', 'created_by').all()
    filterset_fields = ['status', 'payment_status', 'assigned_rider']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    ordering_fields = ['created_at', 'delivery_fee', 'status']
    
    def get_queryset(self):
        """Filter orders based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Riders only see their assigned orders
        if user.is_rider:
            queryset = queryset.filter(assigned_rider=user)
        
        return queryset
    
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
                message="Orders retrieved successfully"
            )
        )


class OrderCreateView(generics.CreateAPIView):
    """
    Create new order (Admin/Manager).
    POST /api/orders/
    """
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAdminOrManager]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        return Response(
            success_response(
                data=OrderSerializer(order).data,
                message="Order created successfully"
            ),
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update order details.
    GET/PATCH /api/orders/{id}/
    """
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.select_related('assigned_rider', 'created_by').prefetch_related('status_logs').all()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response(
            success_response(
                data=serializer.data,
                message="Order details retrieved successfully"
            )
        )
    
    def update(self, request, *args, **kwargs):
        # Only admins can update order details directly
        if not request.user.is_admin:
            return Response(
                error_response(message="Only admins can update order details"),
                status=status.HTTP_403_FORBIDDEN
            )
        
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(
            success_response(
                data=serializer.data,
                message="Order updated successfully"
            )
        )


@api_view(['POST'])
@permission_classes([IsAdminOrManager])
def assign_order_view(request, pk):
    """
    Assign order to a rider.
    POST /api/orders/{id}/assign/
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = OrderAssignmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        order = OrderService.assign_order_to_rider(
            order=order,
            rider_id=serializer.validated_data['rider_id'],
            assigned_by=request.user
        )
        
        return Response(
            success_response(
                data=OrderSerializer(order).data,
                message="Order assigned successfully"
            ),
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            error_response(message=str(e)),
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAdminOrManager])
def reassign_order_view(request, pk):
    """
    Reassign order to a different rider.
    POST /api/orders/{id}/reassign/
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = OrderAssignmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        order = OrderService.reassign_order(
            order=order,
            new_rider_id=serializer.validated_data['rider_id'],
            reassigned_by=request.user
        )
        
        return Response(
            success_response(
                data=OrderSerializer(order).data,
                message="Order reassigned successfully"
            ),
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            error_response(message=str(e)),
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAdminOrManager])
def cancel_order_view(request, pk):
    """
    Cancel an order.
    POST /api/orders/{id}/cancel/
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    reason = request.data.get('reason', '')
    
    try:
        order = OrderService.cancel_order(
            order=order,
            cancelled_by=request.user,
            reason=reason
        )
        
        return Response(
            success_response(
                data=OrderSerializer(order).data,
                message="Order cancelled successfully"
            ),
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            error_response(message=str(e)),
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status_view(request, pk):
    """
    Update order status (Riders update their order status).
    PATCH /api/orders/{id}/status/
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Riders can only update their own assigned orders
    if request.user.is_rider and order.assigned_rider != request.user:
        return Response(
            error_response(message="You can only update orders assigned to you"),
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = OrderStatusUpdateSerializer(
        data=request.data,
        context={'order': order}
    )
    serializer.is_valid(raise_exception=True)
    
    try:
        order = OrderService.update_order_status(
            order=order,
            new_status=serializer.validated_data['status'],
            updated_by=request.user,
            notes=serializer.validated_data.get('notes', ''),
            delivery_proof=serializer.validated_data.get('delivery_proof_image')
        )
        
        return Response(
            success_response(
                data=OrderSerializer(order).data,
                message="Order status updated successfully"
            ),
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            error_response(message=str(e)),
            status=status.HTTP_400_BAD_REQUEST
        )
