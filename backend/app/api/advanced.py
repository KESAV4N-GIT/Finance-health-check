"""
Advanced Features API Router
Endpoints for bookkeeping, tax compliance, forecasting, and recommendations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services.bookkeeping import BookkeepingService
from app.services.tax_compliance import TaxComplianceService, GSTSlabRate
from app.services.forecasting import ForecastingService
from app.services.working_capital import WorkingCapitalService
from app.services.financial_products import FinancialProductsService

router = APIRouter(prefix="/api/advanced", tags=["Advanced Features"])


# ========== Schemas ==========

class TransactionInput(BaseModel):
    description: str
    amount: float

class BatchTransactionInput(BaseModel):
    transactions: List[TransactionInput]

class GSTCalculationInput(BaseModel):
    amount: float
    rate: int = Field(..., description="GST rate: 0, 5, 12, 18, or 28")
    is_interstate: bool = False

class GSTINValidationInput(BaseModel):
    gstin: str

class GSTComplianceInput(BaseModel):
    period: str = Field(..., description="Period in MM-YYYY format")
    gstr1_filed: bool = False
    gstr3b_filed: bool = False
    output_tax: float = 0
    input_tax: float = 0
    liability: float = 0
    filing_date: Optional[str] = None

class ForecastInput(BaseModel):
    historical_data: List[dict]
    months_ahead: int = 6

class WorkingCapitalInput(BaseModel):
    current_assets: float
    current_liabilities: float
    inventory: float
    receivables: float
    payables: float
    annual_revenue: float
    cogs: float
    industry: str = "default"

class ProductRecommendationInput(BaseModel):
    years_in_business: int = 1
    industry: str = "general"
    annual_revenue: float = 0
    current_ratio: float = 1.5
    cash_flow: float = 0
    receivable_days: float = 30
    growth_rate: float = 0
    cash_surplus: float = 0


# ========== Bookkeeping Endpoints ==========

@router.post("/bookkeeping/categorize")
async def categorize_transaction(
    transaction: TransactionInput,
    current_user: User = Depends(get_current_user)
):
    """Automatically categorize a single transaction."""
    service = BookkeepingService()
    result = service.categorize_transaction(
        transaction.description,
        Decimal(str(transaction.amount))
    )
    return result

@router.post("/bookkeeping/batch-categorize")
async def batch_categorize(
    data: BatchTransactionInput,
    current_user: User = Depends(get_current_user)
):
    """Categorize multiple transactions at once."""
    service = BookkeepingService()
    transactions = [{"description": t.description, "amount": t.amount} for t in data.transactions]
    results = service.batch_categorize(transactions)
    return {"categorized": results}

@router.post("/bookkeeping/journal-entry")
async def generate_journal_entry(
    transaction_type: str,
    amount: float,
    description: str,
    category: str,
    current_user: User = Depends(get_current_user)
):
    """Generate a double-entry journal entry."""
    service = BookkeepingService()
    result = service.generate_journal_entry(
        transaction_type,
        Decimal(str(amount)),
        description,
        category
    )
    return result


# ========== Tax Compliance Endpoints ==========

@router.post("/tax/validate-gstin")
async def validate_gstin(
    data: GSTINValidationInput,
    current_user: User = Depends(get_current_user)
):
    """Validate a GSTIN number."""
    service = TaxComplianceService()
    result = service.validate_gstin(data.gstin)
    return result

@router.post("/tax/calculate-gst")
async def calculate_gst(
    data: GSTCalculationInput,
    current_user: User = Depends(get_current_user)
):
    """Calculate GST breakdown (CGST/SGST/IGST)."""
    service = TaxComplianceService()
    
    rate_map = {0: GSTSlabRate.ZERO, 5: GSTSlabRate.FIVE, 12: GSTSlabRate.TWELVE, 
                18: GSTSlabRate.EIGHTEEN, 28: GSTSlabRate.TWENTY_EIGHT}
    
    if data.rate not in rate_map:
        raise HTTPException(status_code=400, detail="Invalid GST rate. Use 0, 5, 12, 18, or 28")
    
    result = service.calculate_gst(
        Decimal(str(data.amount)),
        rate_map[data.rate],
        data.is_interstate
    )
    return result

@router.post("/tax/compliance-check")
async def check_gst_compliance(
    data: GSTComplianceInput,
    current_user: User = Depends(get_current_user)
):
    """Check GST compliance status and get alerts."""
    service = TaxComplianceService()
    result = service.check_gst_compliance(data.model_dump())
    return result

@router.get("/tax/compliance-checklist/{period}")
async def get_compliance_checklist(
    period: str,
    current_user: User = Depends(get_current_user)
):
    """Get tax compliance checklist for a period."""
    service = TaxComplianceService()
    result = service.generate_compliance_checklist(period)
    return {"period": period, "checklist": result}


# ========== Forecasting Endpoints ==========

@router.post("/forecast/cash-flow")
async def forecast_cash_flow(
    data: ForecastInput,
    current_user: User = Depends(get_current_user)
):
    """Generate cash flow forecast based on historical data."""
    service = ForecastingService()
    result = service.forecast_cash_flow(data.historical_data, data.months_ahead)
    return result

@router.post("/forecast/break-even")
async def calculate_break_even(
    fixed_costs: float,
    variable_cost_ratio: float,
    current_revenue: float,
    current_user: User = Depends(get_current_user)
):
    """Calculate break-even point."""
    service = ForecastingService()
    result = service.project_break_even(
        Decimal(str(fixed_costs)),
        Decimal(str(variable_cost_ratio)),
        Decimal(str(current_revenue))
    )
    return result

@router.post("/forecast/scenarios")
async def analyze_scenarios(
    base_revenue: float,
    base_expenses: float,
    current_user: User = Depends(get_current_user)
):
    """Perform scenario analysis (optimistic, base, pessimistic)."""
    service = ForecastingService()
    result = service.scenario_analysis(
        Decimal(str(base_revenue)),
        Decimal(str(base_expenses))
    )
    return result


# ========== Working Capital Endpoints ==========

@router.post("/working-capital/analyze")
async def analyze_working_capital(
    data: WorkingCapitalInput,
    current_user: User = Depends(get_current_user)
):
    """Comprehensive working capital analysis."""
    service = WorkingCapitalService()
    analysis = service.analyze_working_capital(
        Decimal(str(data.current_assets)),
        Decimal(str(data.current_liabilities)),
        Decimal(str(data.inventory)),
        Decimal(str(data.receivables)),
        Decimal(str(data.payables)),
        Decimal(str(data.annual_revenue)),
        Decimal(str(data.cogs))
    )
    recommendations = service.generate_recommendations(analysis, data.industry)
    return {
        "analysis": analysis,
        "recommendations": recommendations
    }

@router.get("/working-capital/financing-needs")
async def calculate_financing_needs(
    growth_rate: float,
    current_wc: float,
    cash_cycle: float,
    current_user: User = Depends(get_current_user)
):
    """Calculate working capital financing needs for growth."""
    service = WorkingCapitalService()
    result = service.calculate_financing_needs(
        growth_rate,
        Decimal(str(current_wc)),
        cash_cycle
    )
    return result


# ========== Financial Products Endpoints ==========

@router.post("/products/recommend")
async def recommend_products(
    data: ProductRecommendationInput,
    current_user: User = Depends(get_current_user)
):
    """Get personalized financial product recommendations."""
    service = FinancialProductsService()
    
    profile = {
        "years_in_business": data.years_in_business,
        "industry": data.industry
    }
    
    metrics = {
        "annual_revenue": data.annual_revenue,
        "current_ratio": data.current_ratio,
        "cash_flow": data.cash_flow,
        "receivable_days": data.receivable_days,
        "growth_rate": data.growth_rate,
        "cash_surplus": data.cash_surplus
    }
    
    result = service.recommend_products(profile, metrics)
    return result

@router.get("/products/compare")
async def compare_products(
    product_ids: str,  # comma-separated
    category: str = "loans",
    current_user: User = Depends(get_current_user)
):
    """Compare financial products side by side."""
    service = FinancialProductsService()
    ids = [p.strip() for p in product_ids.split(",")]
    result = service.compare_products(ids, category)
    return result
