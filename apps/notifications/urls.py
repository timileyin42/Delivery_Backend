from django.urls import path
from .views import (
    NotificationListView,
    mark_as_read_view,
    mark_all_as_read_view,
    delete_notification_view,
    unread_count_view,
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', mark_as_read_view, name='mark-as-read'),
    path('read-all/', mark_all_as_read_view, name='mark-all-as-read'),
    path('<int:pk>/', delete_notification_view, name='delete-notification'),
    path('unread-count/', unread_count_view, name='unread-count'),
]
