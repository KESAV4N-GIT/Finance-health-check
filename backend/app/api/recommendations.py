"""
Recommendations API Endpoints
Handles cost optimization and financial product recommendations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.financial_metrics import FinancialMetrics
from app.schemas.analysis import CostOptimizationResponse, CostOptimizationItem
from app.services.llm_service import LLMAnalyzer

router = APIRouter()


@router.get("/cost-optimization", response_model=CostOptimizationResponse)
async def get_cost_optimization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI-generated cost optimization recommendations.
    """
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(6)
    )
    metrics_list = result.scalars().all()
    
    if not metrics_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found"
        )
    
    llm_analyzer = LLMAnalyzer()
    recommendations = await llm_analyzer.get_cost_optimization(
        metrics_list[0],
        current_user.industry_type.value
    )
    
    return CostOptimizationResponse(**recommendations)


@router.get("/financial-products")
async def get_financial_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommended financial products based on user profile.
    """
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(1)
    )
    metrics = result.scalar_one_or_none()
    
    # Mock product recommendations (in production, would query product database)
    products = [
        {
            "name": "Working Capital Loan",
            "provider": "SBI",
            "type": "loan",
            "interest_rate": "10.5% - 12.5%",
            "amount_range": "₹5L - ₹2Cr",
            "tenure": "12 - 36 months",
            "eligibility_score": 85,
            "features": ["Quick disbursement", "Minimal documentation", "Flexible repayment"],
            "best_for": "Managing cash flow gaps"
        },
        {
            "name": "Business Line of Credit",
            "provider": "HDFC Bank",
            "type": "credit_line",
            "interest_rate": "11% - 14%",
            "amount_range": "₹10L - ₹5Cr",
            "tenure": "Revolving",
            "eligibility_score": 78,
            "features": ["Pay interest only on usage", "Reusable limit", "Digital access"],
            "best_for": "Seasonal businesses"
        },
        {
            "name": "Equipment Finance",
            "provider": "ICICI Bank",
            "type": "loan",
            "interest_rate": "9.5% - 11%",
            "amount_range": "₹3L - ₹3Cr",
            "tenure": "24 - 60 months",
            "eligibility_score": 90,
            "features": ["90% financing", "Asset-backed", "Tax benefits"],
            "best_for": "Capital equipment purchases"
        }
    ]
    
    return {
        "company_name": current_user.company_name,
        "industry": current_user.industry_type.value,
        "products": products,
        "total_products": len(products)
    }
