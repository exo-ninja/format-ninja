from google.cloud import tasks_v2
from app.config import settings
import json


class CloudTasksService:
    """Service for interacting with Google Cloud Tasks."""

    def __init__(self):
        """Initialize the Cloud Tasks client."""
        if settings.use_gcp_service_account:
            # Use service account credentials in development
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                settings.GCP_SERVICE_ACCOUNT_KEY
            )
            self.client = tasks_v2.CloudTasksClient(credentials=credentials)
        else:
            # In production, rely on VM service account
            self.client = tasks_v2.CloudTasksClient()

        self.project = settings.GCP_PROJECT_ID
        self.location = settings.GCP_LOCATION
        self.queue = settings.GCP_TASKS_QUEUE

        # Format parent queue path
        self.parent = self.client.queue_path(self.project, self.location, self.queue)

    def create_task(self, url, payload, task_name=None, delay_seconds=0):
        """
        Create a new task in the queue.

        Args:
            url: The full URL of the endpoint to call
            payload: Dictionary containing the task data
            task_name: Optional unique name for the task
            delay_seconds: Seconds to delay task execution

        Returns:
            The created task
        """
        # Create task
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": url,
                "headers": {
                    "Content-Type": "application/json",
                },
            }
        }

        # Add payload if provided
        if payload:
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            task["http_request"]["body"] = payload.encode()

        # Add task name if provided
        if task_name:
            task["name"] = self.client.task_path(
                self.project, self.location, self.queue, task_name
            )

        # Add delay if specified
        if delay_seconds > 0:
            task["schedule_time"] = {"seconds": int(time.time() + delay_seconds)}

        # Create and return the task
        return self.client.create_task(request={"parent": self.parent, "task": task})

    def create_transform_task(
        self, job_id, source_format, target_format, source_path, config=None
    ):
        """
        Create a transformation task.

        Args:
            job_id: The unique job ID
            source_format: The source file format
            target_format: The target file format
            source_path: Path to the source file in Cloud Storage
            config: Optional transformation configuration

        Returns:
            The created task
        """
        # Determine the processing endpoint
        url = f"{settings.API_BASE_URL}/api/v1/process"

        # Create payload
        payload = {
            "job_id": job_id,
            "source_format": source_format,
            "target_format": target_format,
            "source_path": source_path,
        }

        # Add config if provided
        if config:
            payload["config"] = config

        # Create task with the job_id as the task name for idempotency
        return self.create_task(url, payload, task_name=job_id)
