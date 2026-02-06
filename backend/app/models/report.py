"""
Report Model
Stores generated reports and their export data.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ReportType(str, enum.Enum):
    """Types of reports that can be generated."""
    FINANCIAL_HEALTH = "financial_health"
    RISK_ASSESSMENT = "risk_assessment"
    INVESTOR_READY = "investor_ready"
    TAX_COMPLIANCE = "tax_compliance"
    BENCHMARKING = "benchmarking"
    CASH_FLOW_FORECAST = "cash_flow_forecast"


class ReportStatus(str, enum.Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """Stores generated reports and export data."""
    
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Report details
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Content
    content: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Generation status
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus),
        default=ReportStatus.PENDING,
        nullable=False
    )
    
    # Export
    export_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    export_format: Mapped[str] = mapped_column(String(10), default="pdf", nullable=False)
    
    # Language
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reports")
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, type={self.report_type}, status={self.status})>"
