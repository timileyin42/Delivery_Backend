from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from django.conf import settings
from datetime import timedelta
import logging
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class GCPStorageService:
    """
    Service for handling file uploads to Google Cloud Storage with presigned URLs.
    """
    
    def __init__(self):
        """Initialize GCS client."""
        try:
            # If you have a service account JSON file
            if hasattr(settings, 'GCP_CREDENTIALS_FILE') and settings.GCP_CREDENTIALS_FILE:
                self.client = storage.Client.from_service_account_json(
                    settings.GCP_CREDENTIALS_FILE
                )
            else:
                # Uses application default credentials
                self.client = storage.Client(project=settings.GCP_PROJECT_ID)
            
            self.bucket_name = settings.GCS_BUCKET_NAME
            self.bucket = self.client.bucket(self.bucket_name)
            
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {str(e)}")
            raise
    
    def generate_unique_filename(self, original_filename):
        """
        Generate unique filename to avoid collisions.
        
        Args:
            original_filename: Original file name
        
        Returns:
            str: Unique filename with original extension
        """
        file_extension = Path(original_filename).suffix
        unique_name = f"{uuid.uuid4().hex}{file_extension}"
        return unique_name
    
    def upload_file(self, file_obj, folder="", filename=None):
        """
        Upload file to GCS and return public URL.
        
        Args:
            file_obj: Django UploadedFile object
            folder: Optional folder path in bucket
            filename: Optional custom filename (will be made unique)
        
        Returns:
            dict: {
                'url': str,  # Public URL
                'blob_name': str,  # Full path in bucket
                'filename': str  # Generated filename
            }
        """
        try:
            # Generate unique filename
            if filename:
                filename = self.generate_unique_filename(filename)
            else:
                filename = self.generate_unique_filename(file_obj.name)
            
            # Construct blob path
            blob_name = f"{folder}/{filename}" if folder else filename
            
            # Create blob
            blob = self.bucket.blob(blob_name)
            
            # Set content type
            content_type = file_obj.content_type if hasattr(file_obj, 'content_type') else 'application/octet-stream'
            blob.content_type = content_type
            
            # Upload file
            blob.upload_from_file(file_obj, content_type=content_type)
            
            # Make publicly accessible (optional - remove if you only want presigned URLs)
            # blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            logger.info(f"File uploaded successfully to GCS: {blob_name}")
            
            return {
                'url': public_url,
                'blob_name': blob_name,
                'filename': filename
            }
            
        except GoogleCloudError as e:
            logger.error(f"GCS upload error: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def generate_presigned_url(self, blob_name, expiration_minutes=60):
        """
        Generate presigned URL for secure file access.
        
        Args:
            blob_name: Full path of blob in bucket
            expiration_minutes: URL validity duration in minutes
        
        Returns:
            str: Presigned URL
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Generate signed URL
            url = blob.generate_signed_url(
                version='v4',
                expiration=timedelta(minutes=expiration_minutes),
                method='GET'
            )
            
            logger.info(f"Presigned URL generated for: {blob_name}")
            return url
            
        except GoogleCloudError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def generate_upload_presigned_url(self, blob_name, content_type='image/jpeg', expiration_minutes=15):
        """
        Generate presigned URL for uploading directly from client.
        
        Args:
            blob_name: Desired path in bucket
            content_type: MIME type of file
            expiration_minutes: URL validity duration
        
        Returns:
            dict: {
                'upload_url': str,
                'blob_name': str
            }
        """
        try:
            blob = self.bucket.blob(blob_name)
            
            # Generate signed URL for PUT/POST
            url = blob.generate_signed_url(
                version='v4',
                expiration=timedelta(minutes=expiration_minutes),
                method='PUT',
                content_type=content_type
            )
            
            logger.info(f"Upload presigned URL generated for: {blob_name}")
            
            return {
                'upload_url': url,
                'blob_name': blob_name
            }
            
        except GoogleCloudError as e:
            logger.error(f"Failed to generate upload presigned URL: {str(e)}")
            raise Exception(f"Failed to generate upload presigned URL: {str(e)}")
    
    def delete_file(self, blob_name):
        """
        Delete file from GCS.
        
        Args:
            blob_name: Full path of blob to delete
        
        Returns:
            bool: True if successful
        """
        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            
            logger.info(f"File deleted from GCS: {blob_name}")
            return True
            
        except GoogleCloudError as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False
    
    def file_exists(self, blob_name):
        """
        Check if file exists in GCS.
        
        Args:
            blob_name: Full path of blob
        
        Returns:
            bool: True if exists
        """
        try:
            blob = self.bucket.blob(blob_name)
            return blob.exists()
        except GoogleCloudError:
            return False


# Singleton instance
_gcs_service = None


def get_gcs_service():
    """Get or create GCS service instance."""
    global _gcs_service
    if _gcs_service is None:
        _gcs_service = GCPStorageService()
    return _gcs_service
