"""
Analysis API Endpoints
Handles risk assessment, creditworthiness, and benchmarking.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.financial_metrics import FinancialMetrics
from app.models.risk_assessment import RiskAssessment
from app.models.industry_benchmark import IndustryBenchmark
from app.schemas.analysis import (
    RiskAssessmentResponse,
    BenchmarkingResponse,
    BenchmarkMetric,
    CreditworthinessResponse,
    CreditScoreBreakdown,
    ForecastResponse,
    ForecastDataPoint
)
from app.services.risk_engine import RiskAssessor
from app.services.llm_service import LLMAnalyzer

router = APIRouter()


@router.get("/risk", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    regenerate: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get or generate risk assessment for the user's business.
    
    Set regenerate=true to force a new assessment.
    """
    # Check for existing recent assessment
    if not regenerate:
        result = await db.execute(
            select(RiskAssessment)
            .where(RiskAssessment.user_id == current_user.id)
            .order_by(desc(RiskAssessment.generated_at))
            .limit(1)
        )
        existing = result.scalar_one_or_none()
        
        # Return existing if less than 24 hours old
        if existing and (datetime.utcnow() - existing.generated_at).days < 1:
            return RiskAssessmentResponse.model_validate(existing)
    
    # Get latest financial metrics
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(6)  # Last 6 periods for trend analysis
    )
    metrics_list = result.scalars().all()
    
    if not metrics_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found. Please upload financial statements first."
        )
    
    # Generate new assessment
    risk_assessor = RiskAssessor()
    llm_analyzer = LLMAnalyzer()
    
    assessment_data = await risk_assessor.assess_risk(
        metrics=metrics_list[0],
        historical_metrics=metrics_list,
        industry=current_user.industry_type.value
    )
    
    # Get AI insights
    insights = await llm_analyzer.generate_risk_insights(
        assessment_data,
        current_user.industry_type.value
    )
    
    # Save assessment
    risk_assessment = RiskAssessment(
        user_id=current_user.id,
        overall_risk_score=assessment_data["overall_score"],
        creditworthiness_score=assessment_data["creditworthiness_score"],
        liquidity_risk_score=assessment_data["liquidity_score"],
        solvency_risk_score=assessment_data["solvency_score"],
        operational_risk_score=assessment_data["operational_score"],
        risk_level=assessment_data["risk_level"],
        risk_factors=assessment_data["risk_factors"],
        recommendations=insights["recommendations"],
        insights_summary=insights["summary"],
        cash_flow_forecast=assessment_data.get("forecast")
    )
    
    db.add(risk_assessment)
    await db.flush()
    await db.refresh(risk_assessment)
    
    return RiskAssessmentResponse.model_validate(risk_assessment)


@router.get("/creditworthiness", response_model=CreditworthinessResponse)
async def get_creditworthiness(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed creditworthiness analysis.
    """
    # Get latest metrics
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(1)
    )
    metrics = result.scalar_one_or_none()
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found"
        )
    
    risk_assessor = RiskAssessor()
    credit_data = risk_assessor.calculate_creditworthiness(metrics)
    
    return CreditworthinessResponse(**credit_data)


@router.get("/benchmarking", response_model=BenchmarkingResponse)
async def get_industry_benchmarking(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare user's metrics against industry benchmarks.
    """
    # Get latest metrics
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(1)
    )
    user_metrics = result.scalar_one_or_none()
    
    if not user_metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found"
        )
    
    # Get industry benchmarks
    benchmark_result = await db.execute(
        select(IndustryBenchmark)
        .where(IndustryBenchmark.industry_type == current_user.industry_type.value)
    )
    benchmarks = benchmark_result.scalars().all()
    
    if not benchmarks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No benchmarks available for your industry"
        )
    
    # Build comparison
    metrics_comparison = []
    strengths = []
    weaknesses = []
    
    metric_mapping = {
        "current_ratio": user_metrics.current_ratio,
        "gross_margin": user_metrics.gross_margin,
        "net_margin": user_metrics.net_margin,
        "debt_to_equity": user_metrics.debt_to_equity,
        "roe": user_metrics.roe,
    }
    
    for benchmark in benchmarks:
        if benchmark.metric_name in metric_mapping:
            user_value = metric_mapping[benchmark.metric_name]
            if user_value is not None:
                user_val = float(user_value)
                avg_val = float(benchmark.avg_value)
                p25 = float(benchmark.percentile_25)
                p75 = float(benchmark.percentile_75)
                
                # Calculate percentile rank
                if user_val >= p75:
                    percentile = 75 + int((user_val - p75) / (float(benchmark.max_value) - p75) * 25)
                elif user_val >= avg_val:
                    percentile = 50 + int((user_val - avg_val) / (p75 - avg_val) * 25)
                elif user_val >= p25:
                    percentile = 25 + int((user_val - p25) / (avg_val - p25) * 25)
                else:
                    percentile = int((user_val - float(benchmark.min_value)) / (p25 - float(benchmark.min_value)) * 25)
                
                percentile = max(0, min(100, percentile))
                
                if percentile >= 60:
                    status_str = "above_average"
                    strengths.append(f"Strong {benchmark.metric_name.replace('_', ' ')}")
                elif percentile <= 40:
                    status_str = "below_average"
                    weaknesses.append(f"Improve {benchmark.metric_name.replace('_', ' ')}")
                else:
                    status_str = "average"
                
                metrics_comparison.append(BenchmarkMetric(
                    metric_name=benchmark.metric_name,
                    user_value=user_val,
                    industry_avg=avg_val,
                    percentile_25=p25,
                    percentile_75=p75,
                    percentile_rank=percentile,
                    status=status_str,
                    description=benchmark.description
                ))
    
    # Calculate overall percentile
    if metrics_comparison:
        overall_percentile = sum(m.percentile_rank for m in metrics_comparison) // len(metrics_comparison)
    else:
        overall_percentile = 50
    
    return BenchmarkingResponse(
        industry_type=current_user.industry_type.value,
        company_name=current_user.company_name,
        overall_percentile=overall_percentile,
        metrics=metrics_comparison,
        strengths=strengths[:5],
        weaknesses=weaknesses[:5],
        recommendations=[f"Focus on improving {w}" for w in weaknesses[:3]],
        sample_size=benchmarks[0].sample_size if benchmarks else 0,
        last_updated=benchmarks[0].updated_at if benchmarks else datetime.utcnow()
    )


@router.get("/forecast", response_model=ForecastResponse)
async def get_financial_forecast(
    forecast_type: str = "cash_flow",  # revenue, expenses, cash_flow
    horizon: str = "6_months",  # 3_months, 6_months, 12_months
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get financial forecast with scenario analysis.
    """
    # Get historical data
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(12)
    )
    metrics_list = result.scalars().all()
    
    if len(metrics_list) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 3 months of data for forecasting"
        )
    
    risk_assessor = RiskAssessor()
    forecast = risk_assessor.generate_forecast(
        metrics_list[::-1],  # Chronological order
        forecast_type,
        horizon
    )
    
    return ForecastResponse(**forecast)
