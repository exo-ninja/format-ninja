from google.cloud import storage
from app.config import settings
import os
import uuid


class CloudStorageService:
    """Service for interacting with Google Cloud Storage."""

    def __init__(self):
        """Initialize the Cloud Storage client."""
        if settings.use_gcp_service_account:
            # Use service account credentials in development
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                settings.GCP_SERVICE_ACCOUNT_KEY
            )
            self.client = storage.Client(
                credentials=credentials, project=settings.GCP_PROJECT_ID
            )
        else:
            # In production, rely on VM service account
            self.client = storage.Client()

        self.bucket_name = settings.GCP_STORAGE_BUCKET
        self.bucket = self.client.bucket(self.bucket_name)

    def upload_file(self, file_data, file_format, prefix="uploads"):
        """
        Upload a file to Cloud Storage.

        Args:
            file_data: The file data to upload (bytes or file-like object)
            file_format: The file format (extension)
            prefix: Directory prefix for the file (default: 'uploads')

        Returns:
            The path to the uploaded file in the bucket
        """
        # Generate a unique filename with the correct extension
        filename = f"{uuid.uuid4()}.{file_format}"
        file_path = f"{prefix}/{filename}"

        # Create a blob and upload the file data
        blob = self.bucket.blob(file_path)

        # If file_data is bytes, upload from string
        if isinstance(file_data, bytes):
            blob.upload_from_string(
                file_data, content_type=self._get_content_type(file_format)
            )
        else:
            # Otherwise, upload from a file-like object
            blob.upload_from_file(
                file_data, content_type=self._get_content_type(file_format)
            )

        return file_path

    def download_file(self, file_path):
        """
        Download a file from Cloud Storage.

        Args:
            file_path: The path to the file in the bucket

        Returns:
            The file data as bytes
        """
        blob = self.bucket.blob(file_path)
        return blob.download_as_bytes()

    def get_public_url(self, file_path):
        """
        Get a public URL for a file (if the bucket permits public access).

        Args:
            file_path: The path to the file in the bucket

        Returns:
            The public URL for the file
        """
        return f"https://storage.googleapis.com/{self.bucket_name}/{file_path}"

    def get_signed_url(self, file_path, expiration=3600):
        """
        Get a signed URL for a file with temporary access.

        Args:
            file_path: The path to the file in the bucket
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            A signed URL for the file
        """
        blob = self.bucket.blob(file_path)
        return blob.generate_signed_url(expiration=expiration)

    def delete_file(self, file_path):
        """
        Delete a file from Cloud Storage.

        Args:
            file_path: The path to the file in the bucket
        """
        blob = self.bucket.blob(file_path)
        blob.delete()

    def _get_content_type(self, file_format):
        """
        Get the content type for a file format.

        Args:
            file_format: The file format (extension)

        Returns:
            The content type for the file format
        """
        content_types = {
            "json": "application/json",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xls": "application/vnd.ms-excel",
        }

        return content_types.get(file_format.lower(), "application/octet-stream")
