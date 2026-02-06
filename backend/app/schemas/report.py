"""
Report Schemas
Pydantic models for report generation.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.models.report import ReportType, ReportStatus


class ReportCreate(BaseModel):
    """Schema for report generation request."""
    report_type: ReportType
    title: Optional[str] = None
    language: str = Field(default="en", pattern="^(en|hi)$")
    include_forecast: bool = False
    period_months: int = Field(default=12, ge=1, le=36)


class ReportResponse(BaseModel):
    """Response for report."""
    id: int
    report_type: ReportType
    title: str
    status: ReportStatus
    language: str
    generated_at: datetime
    expires_at: Optional[datetime] = None
    export_path: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReportContent(BaseModel):
    """Full report content."""
    id: int
    report_type: ReportType
    title: str
    company_name: str
    generated_at: datetime
    language: str
    
    # Content sections
    executive_summary: str
    financial_overview: Dict[str, Any]
    key_metrics: Dict[str, Any]
    risk_analysis: Optional[Dict[str, Any]] = None
    recommendations: List[Dict[str, Any]]
    
    # Visualizations data
    charts_data: Optional[Dict[str, Any]] = None


class ReportListResponse(BaseModel):
    """Response with list of reports."""
    items: List[ReportResponse]
    total: int
    page: int = 1
    page_size: int = 20


class ExportRequest(BaseModel):
    """Request for report export."""
    report_id: int
    format: str = Field(default="pdf", pattern="^(pdf|xlsx|html)$")
