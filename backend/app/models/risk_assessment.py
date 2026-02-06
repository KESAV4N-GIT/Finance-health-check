"""
Risk Assessment Model
Stores AI-generated risk assessments and recommendations.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RiskAssessment(Base):
    """Stores risk assessments and AI-generated recommendations."""
    
    __tablename__ = "risk_assessments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Scores (0-100 scale)
    overall_risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    creditworthiness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    liquidity_risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    solvency_risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    operational_risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Risk level classification
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high
    
    # AI-generated content
    risk_factors: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    insights_summary: Mapped[Optional[str]] = mapped_column(nullable=True)
    
    # Forecast data
    cash_flow_forecast: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="risk_assessments")
    
    def __repr__(self) -> str:
        return f"<RiskAssessment(id={self.id}, risk_score={self.overall_risk_score}, level={self.risk_level})>"
