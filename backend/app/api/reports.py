"""
Reports API Endpoints
Handles report generation and export.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.report import Report, ReportType, ReportStatus
from app.models.financial_metrics import FinancialMetrics
from app.models.risk_assessment import RiskAssessment
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportContent,
    ReportListResponse,
    ExportRequest
)
from app.services.report_generator import ReportGenerator

router = APIRouter()


@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_request: ReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new report.
    
    Report types:
    - financial_health: Overall financial health summary
    - risk_assessment: Detailed risk analysis
    - investor_ready: Investor presentation format
    - tax_compliance: GST and tax compliance status
    - benchmarking: Industry comparison report
    - cash_flow_forecast: Cash flow projections
    """
    # Generate title if not provided
    title = report_request.title or f"{report_request.report_type.value.replace('_', ' ').title()} Report"
    
    # Create report record
    report = Report(
        user_id=current_user.id,
        report_type=report_request.report_type,
        title=title,
        language=report_request.language,
        status=ReportStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(report)
    await db.flush()
    await db.refresh(report)
    
    # Queue background generation
    generator = ReportGenerator()
    background_tasks.add_task(
        generator.generate_report_async,
        report_id=report.id,
        user_id=current_user.id,
        report_type=report_request.report_type,
        language=report_request.language,
        include_forecast=report_request.include_forecast
    )
    
    return ReportResponse.model_validate(report)


@router.get("/", response_model=ReportListResponse)
async def list_reports(
    page: int = 1,
    page_size: int = 20,
    report_type: ReportType = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all reports for the current user.
    """
    offset = (page - 1) * page_size
    
    query = select(Report).where(Report.user_id == current_user.id)
    
    if report_type:
        query = query.where(Report.report_type == report_type)
    
    query = query.order_by(desc(Report.generated_at)).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    
    # Get total count
    count_query = select(Report).where(Report.user_id == current_user.id)
    if report_type:
        count_query = count_query.where(Report.report_type == report_type)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return ReportListResponse(
        items=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{report_id}", response_model=ReportContent)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get full report content.
    """
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .where(Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is {report.status.value}. Please wait for completion."
        )
    
    return ReportContent(
        id=report.id,
        report_type=report.report_type,
        title=report.title,
        company_name=current_user.company_name,
        generated_at=report.generated_at,
        language=report.language,
        executive_summary=report.summary or "",
        financial_overview=report.content.get("financial_overview", {}) if report.content else {},
        key_metrics=report.content.get("key_metrics", {}) if report.content else {},
        risk_analysis=report.content.get("risk_analysis") if report.content else None,
        recommendations=report.content.get("recommendations", []) if report.content else [],
        charts_data=report.content.get("charts_data") if report.content else None
    )


@router.get("/{report_id}/export")
async def export_report(
    report_id: int,
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export report as PDF, XLSX, or HTML.
    """
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .where(Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.status != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report not ready for export"
        )
    
    if format not in ["pdf", "xlsx", "html"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Supported: pdf, xlsx, html"
        )
    
    # Generate export file
    generator = ReportGenerator()
    export_path = await generator.export_report(report, format)
    
    # Update report with export path
    report.export_path = export_path
    report.export_format = format
    await db.flush()
    
    return FileResponse(
        path=export_path,
        filename=f"{report.title.replace(' ', '_')}.{format}",
        media_type=f"application/{format}"
    )


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a report.
    """
    result = await db.execute(
        select(Report)
        .where(Report.id == report_id)
        .where(Report.user_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    await db.delete(report)
    await db.flush()
    
    return {"message": "Report deleted successfully"}
