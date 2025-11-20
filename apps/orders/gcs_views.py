from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from apps.users.permissions import IsRider
from apps.common.utils import success_response, error_response
from apps.common.gcp_storage import get_gcs_service
from .models import Order
from .gcs_serializers import DeliveryProofUploadSerializer, DeliveryProofConfirmSerializer


@api_view(['POST'])
@permission_classes([IsRider])
def get_delivery_proof_upload_url_view(request, order_id):
    """
    Generate presigned URL for uploading delivery proof to GCS.
    POST /api/orders/{id}/upload-proof-url/
    Body: {"filename": "proof.jpg", "content_type": "image/jpeg"}
    
    Returns presigned URL for client to upload directly to GCS.
    """
    try:
        order = Order.objects.get(pk=order_id, assigned_rider=request.user)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found or not assigned to you"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DeliveryProofUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    upload_data = serializer.save()
    
    return Response(
        success_response(
            data=upload_data,
            message="Upload URL generated successfully. Upload your file to the URL."
        ),
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsRider])
def confirm_delivery_proof_upload_view(request, order_id):
    """
    Confirm that delivery proof has been uploaded to GCS.
    POST /api/orders/{id}/confirm-proof/
    Body: {"blob_name": "delivery_proofs/xyz.jpg"}
    
    Updates order with the GCS blob reference.
    """
    try:
        order = Order.objects.get(pk=order_id, assigned_rider=request.user)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found or not assigned to you"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = DeliveryProofConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order = serializer.update(order, serializer.validated_data)
    
    # Generate presigned viewing URL
    gcs_service = get_gcs_service()
    viewing_url = gcs_service.generate_presigned_url(
        blob_name=order.delivery_proof_image,
        expiration_minutes=60
    )
    
    return Response(
        success_response(
            data={
                'order_id': order.id,
                'delivery_proof_url': viewing_url,
                'message': 'Delivery proof saved successfully'
            },
            message="Delivery proof confirmed"
        ),
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([IsRider])
def get_delivery_proof_url_view(request, order_id):
    """
    Get presigned URL to view delivery proof image.
    GET /api/orders/{id}/delivery-proof/
    
    Returns temporary presigned URL for viewing the image.
    """
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response(
            error_response(message="Order not found"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not order.delivery_proof_image:
        return Response(
            error_response(message="No delivery proof available for this order"),
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Generate presigned viewing URL
    gcs_service = get_gcs_service()
    viewing_url = gcs_service.generate_presigned_url(
        blob_name=order.delivery_proof_image,
        expiration_minutes=60
    )
    
    return Response(
        success_response(
            data={
                'delivery_proof_url': viewing_url,
                'expires_in_minutes': 60
            },
            message="Delivery proof URL generated"
        ),
        status=status.HTTP_200_OK
    )
