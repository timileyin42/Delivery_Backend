from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Notification
from .serializers import NotificationSerializer
from apps.common.utils import success_response, error_response


class NotificationListView(generics.ListAPIView):
    """
    List user notifications.
    GET /api/notifications/
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by read status if provided
        is_read = request.query_params.get('is_read')
        if is_read is not None:
            is_read = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read)
        
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            success_response(
                data=serializer.data,
                message="Notifications retrieved successfully"
            )
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_as_read_view(request, pk):
    """
    Mark notification as read.
    PATCH /api/notifications/{id}/read/
    """
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response(
            success_response(
                data=NotificationSerializer(notification).data,
                message="Notification marked as read"
            ),
            status=status.HTTP_200_OK
        )
    except Notification.DoesNotExist:
        return Response(
            error_response(message="Notification not found"),
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_as_read_view(request):
    """
    Mark all notifications as read.
    POST /api/notifications/read-all/
    """
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response(
        success_response(
            data={'count': count},
            message=f"{count} notifications marked as read"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification_view(request, pk):
    """
    Delete a notification.
    DELETE /api/notifications/{id}/
    """
    try:
        notification = Notification.objects.get(pk=pk, recipient=request.user)
        notification.delete()
        
        return Response(
            success_response(message="Notification deleted successfully"),
            status=status.HTTP_200_OK
        )
    except Notification.DoesNotExist:
        return Response(
            error_response(message="Notification not found"),
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count_view(request):
    """
    Get count of unread notifications.
    GET /api/notifications/unread-count/
    """
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()
    
    return Response(
        success_response(
            data={'count': count},
            message="Unread count retrieved successfully"
        ),
        status=status.HTTP_200_OK
    )
