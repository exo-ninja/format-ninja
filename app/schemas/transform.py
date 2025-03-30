from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class FileFormatEnum(str, Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class TransformationRequest(BaseModel):
    source_format: FileFormatEnum
    target_format: FileFormatEnum
    config: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "source_format": "json",
                "target_format": "csv",
                "config": {"delimiter": ",", "headers": True},
            }
        }


class TransformationResponse(BaseModel):
    job_id: str
    status: str
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "pending",
                "message": "Transformation job submitted successfully",
            }
        }


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    result_url: Optional[str] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "status": "completed",
                "created_at": "2025-03-30T12:00:00Z",
                "updated_at": "2025-03-30T12:01:05Z",
                "result_url": "https://storage.googleapis.com/format-ninja-bucket/results/result.csv",
            }
        }
