"""
Financial Data Model
Stores uploaded financial documents and their processing status.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class FileType(str, enum.Enum):
    """Supported file types for upload."""
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


class ProcessingStatus(str, enum.Enum):
    """File processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FinancialData(Base):
    """Stores uploaded financial documents and processing status."""
    
    __tablename__ = "financial_data"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[FileType] = mapped_column(Enum(FileType), nullable=False)
    encrypted_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(nullable=False)
    
    # Processing
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus),
        default=ProcessingStatus.PENDING,
        nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Metadata (column mappings, detected format, etc.)
    file_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Extracted data summary
    record_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    date_range_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    date_range_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    upload_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="financial_data")
    
    def __repr__(self) -> str:
        return f"<FinancialData(id={self.id}, file={self.original_filename}, status={self.processing_status})>"
