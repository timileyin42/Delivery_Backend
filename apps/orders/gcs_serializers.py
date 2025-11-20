from rest_framework import serializers
from .models import Order
from apps.common.gcp_storage import get_gcs_service


class DeliveryProofUploadSerializer(serializers.Serializer):
    """
    Serializer for generating presigned upload URL for delivery proof.
    """
    filename = serializers.CharField(max_length=255)
    content_type = serializers.CharField(default='image/jpeg')
    
    def validate_content_type(self, value):
        """Validate that content type is an image."""
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if value not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid content type. Allowed types: {', '.join(allowed_types)}"
            )
        return value
    
    def create(self, validated_data):
        """Generate presigned URL for upload."""
        gcs_service = get_gcs_service()
        
        # Generate unique filename
        unique_filename = gcs_service.generate_unique_filename(validated_data['filename'])
        blob_name = f"delivery_proofs/{unique_filename}"
        
        # Generate upload URL
        upload_data = gcs_service.generate_upload_presigned_url(
            blob_name=blob_name,
            content_type=validated_data['content_type'],
            expiration_minutes=15
        )
        
        return {
            'upload_url': upload_data['upload_url'],
            'blob_name': upload_data['blob_name'],
            'filename': unique_filename
        }


class DeliveryProofConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming delivery proof upload and updating order.
    """
    blob_name = serializers.CharField(max_length=500)
    
    def validate_blob_name(self, value):
        """Verify that file exists in GCS."""
        gcs_service = get_gcs_service()
        if not gcs_service.file_exists(value):
            raise serializers.ValidationError("File not found in storage")
        return value
    
    def update(self, instance, validated_data):
        """Update order with delivery proof blob name."""
        # Store the GCS blob name/path
        instance.delivery_proof_image = validated_data['blob_name']
        instance.save()
        return instance
