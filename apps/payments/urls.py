from django.urls import path
from .views import (
    initialize_payment_view,
    verify_payment_view,
    paystack_webhook_view,
)

app_name = 'payments'

urlpatterns = [
    path('initialize/', initialize_payment_view, name='initialize-payment'),
    path('verify/', verify_payment_view, name='verify-payment'),
    path('webhook/', paystack_webhook_view, name='paystack-webhook'),
]
