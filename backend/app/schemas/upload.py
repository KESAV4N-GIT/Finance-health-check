"""
Upload Schemas
Pydantic models for file upload operations.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.models.financial_data import FileType, ProcessingStatus


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    id: int
    original_filename: str
    file_type: FileType
    file_size_bytes: int
    processing_status: ProcessingStatus
    upload_date: datetime
    message: str = "File uploaded successfully"
    
    class Config:
        from_attributes = True


class UploadHistoryItem(BaseModel):
    """Single item in upload history."""
    id: int
    original_filename: str
    file_type: FileType
    file_size_bytes: int
    processing_status: ProcessingStatus
    upload_date: datetime
    processed_at: Optional[datetime] = None
    record_count: Optional[int] = None
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class UploadHistoryResponse(BaseModel):
    """Response with list of uploaded files."""
    items: List[UploadHistoryItem]
    total: int
    page: int = 1
    page_size: int = 20


class ProcessingStatusResponse(BaseModel):
    """Response for file processing status check."""
    id: int
    processing_status: ProcessingStatus
    error_message: Optional[str] = None
    record_count: Optional[int] = None
    processed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class FileValidationResponse(BaseModel):
    """Response for file validation."""
    is_valid: bool
    file_type: Optional[FileType] = None
    detected_format: Optional[str] = None
    column_count: Optional[int] = None
    row_count: Optional[int] = None
    errors: List[str] = []
    warnings: List[str] = []
