"""
Analysis Schemas
Pydantic models for risk assessment and benchmarking.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RiskFactor(BaseModel):
    """Individual risk factor."""
    name: str
    severity: str = Field(..., pattern="^(low|medium|high|critical)$")
    description: str
    impact_area: str
    recommendation: Optional[str] = None


class Recommendation(BaseModel):
    """AI-generated recommendation."""
    title: str
    description: str
    priority: str = Field(..., pattern="^(low|medium|high)$")
    potential_savings: Optional[float] = None
    implementation_effort: Optional[str] = None
    category: str  # cost_reduction, revenue_growth, risk_mitigation


class RiskAssessmentResponse(BaseModel):
    """Response for risk assessment."""
    id: int
    overall_risk_score: int = Field(..., ge=0, le=100)
    creditworthiness_score: int = Field(..., ge=0, le=100)
    risk_level: str  # low, medium, high
    
    # Component scores
    liquidity_risk_score: int
    solvency_risk_score: int
    operational_risk_score: int
    
    # Details
    risk_factors: List[RiskFactor]
    recommendations: List[Recommendation]
    insights_summary: Optional[str] = None
    
    # Forecast
    cash_flow_forecast: Optional[Dict[str, Any]] = None
    
    generated_at: datetime
    
    class Config:
        from_attributes = True


class BenchmarkMetric(BaseModel):
    """Single benchmark comparison metric."""
    metric_name: str
    user_value: float
    industry_avg: float
    percentile_25: float
    percentile_75: float
    percentile_rank: int  # User's percentile (0-100)
    status: str  # above_average, average, below_average
    description: Optional[str] = None


class BenchmarkingResponse(BaseModel):
    """Response for industry benchmarking."""
    industry_type: str
    company_name: str
    overall_percentile: int
    
    # Metrics comparison
    metrics: List[BenchmarkMetric]
    
    # Summary
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    
    # Metadata
    sample_size: int
    last_updated: datetime


class CreditScoreBreakdown(BaseModel):
    """Credit score component breakdown."""
    component: str
    score: int
    weight: float
    description: str


class CreditworthinessResponse(BaseModel):
    """Response for creditworthiness analysis."""
    overall_score: int = Field(..., ge=0, le=100)
    grade: str  # A, B, C, D, F
    
    # Breakdown
    components: List[CreditScoreBreakdown]
    
    # Factors
    positive_factors: List[str]
    negative_factors: List[str]
    improvement_suggestions: List[str]
    
    # Loan eligibility
    estimated_loan_amount: Optional[float] = None
    estimated_interest_rate: Optional[str] = None


class CostOptimizationItem(BaseModel):
    """Single cost optimization opportunity."""
    category: str
    current_spend: float
    potential_savings: float
    savings_percentage: float
    recommendation: str
    implementation_steps: List[str]
    difficulty: str  # easy, medium, hard


class CostOptimizationResponse(BaseModel):
    """Response for cost optimization analysis."""
    total_current_expenses: float
    total_potential_savings: float
    savings_percentage: float
    
    opportunities: List[CostOptimizationItem]
    
    # AI insights
    summary: str
    priority_actions: List[str]


class ForecastDataPoint(BaseModel):
    """Single forecast data point."""
    period: str
    value: float
    confidence_low: float
    confidence_high: float


class ForecastResponse(BaseModel):
    """Response for financial forecasting."""
    forecast_type: str  # revenue, expenses, cash_flow
    forecast_horizon: str  # 3_months, 6_months, 12_months
    
    # Scenarios
    expected_case: List[ForecastDataPoint]
    best_case: List[ForecastDataPoint]
    worst_case: List[ForecastDataPoint]
    
    # Summary
    trend: str  # growing, stable, declining
    growth_rate: Optional[float] = None
    key_assumptions: List[str]
    risks: List[str]
