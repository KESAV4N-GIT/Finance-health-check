"""
User Model
Stores user account information and authentication data.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.database import Base


class IndustryType(str, enum.Enum):
    """Supported industry types for benchmarking."""
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    AGRICULTURE = "agriculture"
    SERVICES = "services"
    LOGISTICS = "logistics"
    ECOMMERCE = "ecommerce"


class User(Base):
    """User model for authentication and profile."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry_type: Mapped[IndustryType] = mapped_column(
        Enum(IndustryType),
        default=IndustryType.SERVICES,
        nullable=False
    )
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=datetime.utcnow,
        nullable=True
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    financial_data: Mapped[List["FinancialData"]] = relationship(
        "FinancialData",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    financial_metrics: Mapped[List["FinancialMetrics"]] = relationship(
        "FinancialMetrics",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    risk_assessments: Mapped[List["RiskAssessment"]] = relationship(
        "RiskAssessment",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    gst_data: Mapped[List["GSTData"]] = relationship(
        "GSTData",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    api_integrations: Mapped[List["APIIntegration"]] = relationship(
        "APIIntegration",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    reports: Mapped[List["Report"]] = relationship(
        "Report",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, company={self.company_name})>"
