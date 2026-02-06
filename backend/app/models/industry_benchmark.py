"""
Industry Benchmark Model
Stores industry-standard metrics for comparison.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class IndustryBenchmark(Base):
    """Industry benchmark data for comparison analysis."""
    
    __tablename__ = "industry_benchmarks"
    
    industry_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Statistical values
    avg_value: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    median_value: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    percentile_25: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    percentile_75: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    min_value: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    max_value: Mapped[Decimal] = mapped_column(Numeric(15, 4), nullable=False)
    
    # Metadata
    sample_size: Mapped[int] = mapped_column(nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="ratio", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('industry_type', 'metric_name'),
    )
    
    def __repr__(self) -> str:
        return f"<IndustryBenchmark(industry={self.industry_type}, metric={self.metric_name})>"
