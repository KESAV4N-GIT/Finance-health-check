"""
GST Data Model
Stores GST compliance and tax filing data.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class ComplianceStatus(str, enum.Enum):
    """GST compliance status."""
    COMPLIANT = "compliant"
    PENDING = "pending"
    OVERDUE = "overdue"
    NOT_APPLICABLE = "not_applicable"


class GSTData(Base):
    """Stores GST compliance and tax filing data."""
    
    __tablename__ = "gst_data"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # GST Registration
    gst_number: Mapped[str] = mapped_column(String(20), nullable=False)  # Should be encrypted
    registration_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Filing Period
    filing_period: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "Jan 2026"
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Tax Amounts
    output_tax: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    input_tax_credit: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    net_tax_liability: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Compliance
    compliance_status: Mapped[ComplianceStatus] = mapped_column(
        Enum(ComplianceStatus),
        default=ComplianceStatus.PENDING,
        nullable=False
    )
    filing_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    filed_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    last_sync: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="gst_data")
    
    def __repr__(self) -> str:
        return f"<GSTData(id={self.id}, period={self.filing_period}, status={self.compliance_status})>"
