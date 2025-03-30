from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.db.models import TransformationJob, TransformationStatus, FileFormat
from app.utils.cloud_storage import CloudStorageService
from app.utils.cloud_tasks import CloudTasksService
from app.schemas.transform import (
    TransformationRequest,
    TransformationResponse,
    JobStatusResponse,
)
from app.config import settings

router = APIRouter(tags=["transformations"])

# Initialize services
storage_service = CloudStorageService()
tasks_service = CloudTasksService()


@router.post("/transform", response_model=TransformationResponse)
async def transform_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source_format: FileFormat = Form(...),
    target_format: FileFormat = Form(...),
    db: Session = Depends(get_db),
):
    """
    Submit a file for transformation
    - Uploads file to Cloud Storage
    - Creates a job record
    - Enqueues a task for processing
    """
    # Validate format conversion is supported
    if not _is_supported_conversion(source_format, target_format):
        raise HTTPException(
            status_code=400,
            detail=f"Conversion from {source_format} to {target_format} is not supported",
        )

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    try:
        # Read file content
        file_content = await file.read()

        # Upload to Cloud Storage
        file_extension = source_format.value.lower()
        file_path = storage_service.upload_file(
            file_data=file_content, file_format=file_extension
        )

        # Create job record in database
        job = TransformationJob(
            id=uuid.UUID(job_id),
            job_id=job_id,
            source_format=source_format,
            target_format=target_format,
            source_file_path=file_path,
            status=TransformationStatus.PENDING,
        )
        db.add(job)
        db.commit()

        # Enqueue transformation task
        tasks_service.create_transform_task(
            job_id=job_id,
            source_format=source_format.value,
            target_format=target_format.value,
            source_path=file_path,
        )

        return TransformationResponse(
            job_id=job_id,
            status=TransformationStatus.PENDING.value,
            message="Transformation job submitted successfully",
        )

    except Exception as e:
        # Roll back any changes if there was an error
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error submitting transformation: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status of a transformation job
    """
    job = db.query(TransformationJob).filter(TransformationJob.job_id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    response = JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )

    # Include download URL if job is completed
    if job.status == TransformationStatus.COMPLETED and job.result_file_path:
        # Generate a signed URL with 1-hour expiration
        response.result_url = storage_service.get_signed_url(
            file_path=job.result_file_path, expiration=3600
        )

    # Include error message if job failed
    if job.status == TransformationStatus.FAILED and job.error_message:
        response.error = job.error_message

    return response


@router.post("/process", include_in_schema=False)
async def process_transformation(request: dict, db: Session = Depends(get_db)):
    """
    Process transformation task (called by Cloud Tasks)
    - This endpoint should not be called directly by users
    """
    job_id = request.get("job_id")
    source_format = request.get("source_format")
    target_format = request.get("target_format")
    source_path = request.get("source_path")
    config = request.get("config")

    if not all([job_id, source_format, target_format, source_path]):
        return JSONResponse(
            status_code=400, content={"error": "Missing required fields"}
        )

    try:
        # Get job from database
        job = (
            db.query(TransformationJob)
            .filter(TransformationJob.job_id == job_id)
            .first()
        )

        if not job:
            return JSONResponse(status_code=404, content={"error": "Job not found"})

        # Update job status to processing
        job.status = TransformationStatus.PROCESSING
        db.commit()

        # Download file from Cloud Storage
        file_content = storage_service.download_file(source_path)

        # Perform transformation based on formats
        if source_format == "json" and target_format == "csv":
            from app.utils.json_converter import to_csv

            result = to_csv(file_content.decode("utf-8"), config)
            result_extension = "csv"
        elif source_format == "csv" and target_format == "json":
            from app.utils.csv_converter import to_json

            result = to_json(file_content.decode("utf-8"), config)
            result_extension = "json"
        else:
            raise ValueError(
                f"Unsupported transformation: {source_format} to {target_format}"
            )

        # Upload result to Cloud Storage
        result_path = storage_service.upload_file(
            file_data=result.encode("utf-8"),
            file_format=result_extension,
            prefix="results",
        )

        # Update job with success status
        job.status = TransformationStatus.COMPLETED
        job.result_file_path = result_path
        db.commit()

        return JSONResponse(
            status_code=200, content={"status": "success", "job_id": job_id}
        )

    except Exception as e:
        # Update job with error status
        if job:
            job.status = TransformationStatus.FAILED
            job.error_message = str(e)
            db.commit()

        return JSONResponse(
            status_code=500,
            content={"error": f"Error processing transformation: {str(e)}"},
        )


def _is_supported_conversion(source: FileFormat, target: FileFormat) -> bool:
    """Check if the conversion is supported"""
    supported_conversions = [
        (FileFormat.JSON, FileFormat.CSV),
        (FileFormat.CSV, FileFormat.JSON),
    ]

    return (source, target) in supported_conversions
