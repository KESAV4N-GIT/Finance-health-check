"""
File Upload API Endpoints
Handles CSV, XLSX, and PDF file uploads and processing.
"""
import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.financial_data import FinancialData, FileType, ProcessingStatus
from app.schemas.upload import (
    FileUploadResponse,
    UploadHistoryResponse,
    UploadHistoryItem,
    ProcessingStatusResponse,
    FileValidationResponse
)
from app.services.file_processor import FileProcessor

router = APIRouter()


def get_file_type(filename: str) -> Optional[FileType]:
    """Determine file type from extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    try:
        return FileType(ext)
    except ValueError:
        return None


@router.post("/", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a financial statement file for processing.
    
    Supported formats: CSV, XLSX, PDF
    Maximum file size: 10MB
    """
    # Validate file type
    file_type = get_file_type(file.filename)
    if not file_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.allowed_extensions_list)}"
        )
    
    # Read and validate file size
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
        )
    
    # Create upload directory if needed
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file (encrypted)
    processor = FileProcessor()
    encrypted_path = await processor.save_encrypted_file(
        content=content,
        filename=file.filename,
        user_id=current_user.id
    )
    
    # Create database record
    financial_data = FinancialData(
        user_id=current_user.id,
        original_filename=file.filename,
        file_type=file_type,
        encrypted_path=encrypted_path,
        file_size_bytes=len(content),
        processing_status=ProcessingStatus.PENDING
    )
    
    db.add(financial_data)
    await db.flush()
    await db.refresh(financial_data)
    
    # Queue background processing
    background_tasks.add_task(
        processor.process_file_async,
        file_id=financial_data.id,
        encrypted_path=encrypted_path,
        file_type=file_type
    )
    
    return FileUploadResponse(
        id=financial_data.id,
        original_filename=financial_data.original_filename,
        file_type=financial_data.file_type,
        file_size_bytes=financial_data.file_size_bytes,
        processing_status=financial_data.processing_status,
        upload_date=financial_data.upload_date,
        message="File uploaded successfully. Processing started."
    )


@router.post("/validate", response_model=FileValidationResponse)
async def validate_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Validate a file without uploading it.
    
    Returns validation results including detected format and any errors.
    """
    file_type = get_file_type(file.filename)
    
    if not file_type:
        return FileValidationResponse(
            is_valid=False,
            errors=[f"Unsupported file type. Allowed: {', '.join(settings.allowed_extensions_list)}"]
        )
    
    content = await file.read()
    
    if len(content) > settings.max_file_size_bytes:
        return FileValidationResponse(
            is_valid=False,
            file_type=file_type,
            errors=[f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"]
        )
    
    # Validate file content
    processor = FileProcessor()
    validation_result = await processor.validate_file(content, file_type)
    
    return validation_result


@router.get("/history", response_model=UploadHistoryResponse)
async def get_upload_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get upload history for the current user.
    """
    offset = (page - 1) * page_size
    
    # Query uploads
    query = (
        select(FinancialData)
        .where(FinancialData.user_id == current_user.id)
        .where(FinancialData.is_deleted == False)
        .order_by(desc(FinancialData.upload_date))
        .offset(offset)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    uploads = result.scalars().all()
    
    # Get total count
    count_query = (
        select(FinancialData)
        .where(FinancialData.user_id == current_user.id)
        .where(FinancialData.is_deleted == False)
    )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return UploadHistoryResponse(
        items=[UploadHistoryItem.model_validate(u) for u in uploads],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/status/{file_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check processing status of an uploaded file.
    """
    result = await db.execute(
        select(FinancialData)
        .where(FinancialData.id == file_id)
        .where(FinancialData.user_id == current_user.id)
    )
    file_data = result.scalar_one_or_none()
    
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return ProcessingStatusResponse(
        id=file_data.id,
        processing_status=file_data.processing_status,
        error_message=file_data.error_message,
        record_count=file_data.record_count,
        processed_at=file_data.processed_at,
        metadata=file_data.metadata
    )


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete an uploaded file.
    """
    result = await db.execute(
        select(FinancialData)
        .where(FinancialData.id == file_id)
        .where(FinancialData.user_id == current_user.id)
    )
    file_data = result.scalar_one_or_none()
    
    if not file_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file_data.is_deleted = True
    file_data.deleted_at = datetime.utcnow()
    await db.flush()
    
    return {"message": "File deleted successfully"}
