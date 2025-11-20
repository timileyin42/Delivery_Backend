from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status as http_status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import HttpResponse

from .models import Transaction
from .serializers import PaymentInitializationSerializer, TransactionSerializer
from .services import PaystackService
from apps.orders.models import Order
from apps.common.utils import success_response, error_response


@api_view(['POST'])
def initialize_payment_view(request):
    """
    Initialize payment transaction.
    POST /api/payments/initialize/
    """
    serializer = PaymentInitializationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    order_id = serializer.validated_data['order_id']
    email = serializer.validated_data['email']
    callback_url = serializer.validated_data.get('callback_url')
    
    try:
        order = Order.objects.get(pk=order_id)
        
        # Create transaction record
        transaction = Transaction.objects.create(
            order=order,
            amount=order.delivery_fee,
            metadata={'order_id': order.id, 'order_number': order.order_number}
        )
        
        # Initialize with Paystack
        paystack_data = PaystackService.initialize_transaction(
            email=email,
            amount=float(transaction.amount),
            reference=transaction.reference,
            callback_url=callback_url,
            metadata=transaction.metadata
        )
        
        # Update transaction with Paystack data
        transaction.authorization_url = paystack_data.get('authorization_url', '')
        transaction.access_code = paystack_data.get('access_code', '')
        transaction.paystack_reference = paystack_data.get('reference', transaction.reference)
        transaction.save()
        
        return Response(
            success_response(
                data={
                    'transaction': TransactionSerializer(transaction).data,
                    'authorization_url': transaction.authorization_url,
                    'access_code': transaction.access_code
                },
                message="Payment initialized successfully"
            ),
            status=http_status.HTTP_201_CREATED
        )
    
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found"),
            status=http_status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            error_response(message=str(e)),
            status=http_status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
def verify_payment_view(request):
    """
    Verify payment transaction.
    GET /api/payments/verify/?reference=xxx
    """
    reference = request.query_params.get('reference')
    
    if not reference:
        return Response(
            error_response(message="Reference parameter is required"),
            status=http_status.HTTP_400_BAD_REQUEST
        )
    
    try:
        transaction = Transaction.objects.get(reference=reference)
        
        # Verify with Paystack
        paystack_data = PaystackService.verify_transaction(reference)
        
        # Update transaction
        if paystack_data['status'] == 'success':
            transaction.status = Transaction.Status.SUCCESS
            transaction.paid_at = timezone.now()
            transaction.payment_method = paystack_data.get('channel', '')
            transaction.metadata.update(paystack_data)
            
            # Update order payment status
            transaction.order.payment_status = Order.PaymentStatus.PAID
            transaction.order.save()
        else:
            transaction.status = Transaction.Status.FAILED
        
        transaction.save()
        
        return Response(
            success_response(
                data=TransactionSerializer(transaction).data,
                message="Payment verified successfully"
            ),
            status=http_status.HTTP_200_OK
        )
    
    except Transaction.DoesNotExist:
        return Response(
            error_response(message="Transaction not found"),
            status=http_status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            error_response(message=str(e)),
            status=http_status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def paystack_webhook_view(request):
    """
    Handle Paystack webhook events.
    POST /api/payments/webhook/
    """
    # Verify signature
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
    
    if not PaystackService.verify_webhook_signature(request.body, signature):
        return HttpResponse('Invalid signature', status=400)
    
    event_data = request.data
    event_type = event_data.get('event')
    
    if event_type == 'charge.success':
        data = event_data.get('data', {})
        reference = data.get('reference')
        
        try:
            transaction = Transaction.objects.get(reference=reference)
            
            if transaction.status != Transaction.Status.SUCCESS:
                transaction.status = Transaction.Status.SUCCESS
                transaction.paid_at = timezone.now()
                transaction.payment_method = data.get('channel', '')
                transaction.metadata.update(data)
                transaction.save()
                
                # Update order
                transaction.order.payment_status = Order.PaymentStatus.PAID
                transaction.order.save()
        
        except Transaction.DoesNotExist:
            pass
    
    return HttpResponse('OK', status=200)
