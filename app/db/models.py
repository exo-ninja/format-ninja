from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.database import Base

import enum


class TransformationStatus(enum.Enum):
    """Status of a transformation job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileFormat(enum.Enum):
    """Supported file formats."""

    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class TransformationJob(Base):
    """Model for tracking transformation jobs."""

    __tablename__ = "transformation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # For Cloud Tasks reference
    job_id = Column(String, unique=True, index=True, nullable=False)

    source_format = Column(Enum(FileFormat), nullable=False)
    target_format = Column(Enum(FileFormat), nullable=False)

    status = Column(
        Enum(TransformationStatus), default=TransformationStatus.PENDING, nullable=False
    )
    error_message = Column(Text, nullable=True)

    # Storing files as objects in cloud storage
    source_file_path = Column(String, nullable=True)
    result_file_path = Column(String, nullable=True)

    # Configuration for the transformation
    job_config = Column(JSON, nullable=True)

    # Additional metadata about the job
    job_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
