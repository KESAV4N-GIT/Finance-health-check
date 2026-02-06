"""
Financial Data API Endpoints
Handles financial metrics, cash flow, and expense data.
"""
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.financial_metrics import FinancialMetrics
from app.schemas.financial import (
    FinancialSummary,
    MetricsResponse,
    CashFlowResponse,
    CashFlowItem,
    ExpenseBreakdownResponse,
    ExpenseCategory,
    FinancialRatios,
    TransactionCreate,
    TransactionResponse
)
from app.services.analysis_engine import FinancialAnalyzer

router = APIRouter()


@router.get("/summary", response_model=FinancialSummary)
async def get_financial_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get high-level financial summary for dashboard.
    
    Includes key metrics, ratios, and health score.
    """
    # Get latest metrics
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(2)
    )
    metrics_list = result.scalars().all()
    
    if not metrics_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found. Please upload financial statements first."
        )
    
    current = metrics_list[0]
    previous = metrics_list[1] if len(metrics_list) > 1 else None
    
    # Calculate changes from previous period
    revenue_change = None
    expense_change = None
    profit_change = None
    
    if previous and previous.total_revenue > 0:
        revenue_change = float((current.total_revenue - previous.total_revenue) / previous.total_revenue * 100)
    if previous and previous.total_expenses > 0:
        expense_change = float((current.total_expenses - previous.total_expenses) / previous.total_expenses * 100)
    if previous and previous.net_profit != 0:
        profit_change = float((current.net_profit - previous.net_profit) / abs(previous.net_profit) * 100)
    
    # Calculate health score
    analyzer = FinancialAnalyzer()
    health_score, health_status = analyzer.calculate_health_score(current)
    
    # Calculate profit margin
    profit_margin = 0.0
    if current.total_revenue > 0:
        profit_margin = float(current.net_profit / current.total_revenue * 100)
    
    return FinancialSummary(
        total_revenue=current.total_revenue,
        total_expenses=current.total_expenses,
        net_profit=current.net_profit,
        profit_margin=profit_margin,
        current_cash=current.operating_cash_flow,
        operating_cash_flow=current.operating_cash_flow,
        current_ratio=float(current.current_ratio) if current.current_ratio else None,
        debt_to_equity=float(current.debt_to_equity) if current.debt_to_equity else None,
        revenue_change=revenue_change,
        expense_change=expense_change,
        profit_change=profit_change,
        health_score=health_score,
        health_status=health_status,
        period_label=current.period_label,
        last_updated=current.updated_at or current.created_at
    )


@router.get("/metrics", response_model=list[MetricsResponse])
async def get_metrics(
    periods: int = Query(default=12, ge=1, le=36),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get financial metrics for specified number of periods.
    """
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(periods)
    )
    metrics_list = result.scalars().all()
    
    response = []
    for m in metrics_list:
        response.append(MetricsResponse(
            id=m.id,
            period_label=m.period_label,
            period_start=m.period_start,
            period_end=m.period_end,
            total_revenue=m.total_revenue,
            gross_profit=m.gross_profit,
            operating_income=m.operating_income,
            net_profit=m.net_profit,
            total_expenses=m.total_expenses,
            cost_of_goods_sold=m.cost_of_goods_sold,
            operating_expenses=m.operating_expenses,
            ratios=FinancialRatios(
                current_ratio=float(m.current_ratio) if m.current_ratio else None,
                quick_ratio=float(m.quick_ratio) if m.quick_ratio else None,
                gross_margin=float(m.gross_margin) if m.gross_margin else None,
                operating_margin=float(m.operating_margin) if m.operating_margin else None,
                net_margin=float(m.net_margin) if m.net_margin else None,
                debt_to_equity=float(m.debt_to_equity) if m.debt_to_equity else None,
                roe=float(m.roe) if m.roe else None,
                roa=float(m.roa) if m.roa else None,
            )
        ))
    
    return response


@router.get("/cash-flow", response_model=CashFlowResponse)
async def get_cash_flow(
    periods: int = Query(default=12, ge=1, le=24),
    include_forecast: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cash flow analysis with optional forecast.
    """
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(periods)
    )
    metrics_list = result.scalars().all()
    
    if not metrics_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found"
        )
    
    current = metrics_list[0]
    historical = []
    
    for m in metrics_list:
        historical.append(CashFlowItem(
            period=m.period_label,
            operating=m.operating_cash_flow,
            investing=m.investing_cash_flow,
            financing=m.financing_cash_flow,
            net=m.net_cash_flow
        ))
    
    # Determine trend
    if len(metrics_list) >= 3:
        recent_avg = sum(float(m.net_cash_flow) for m in metrics_list[:3]) / 3
        older_avg = sum(float(m.net_cash_flow) for m in metrics_list[-3:]) / 3
        
        if recent_avg > older_avg * 1.1:
            trend = "increasing"
        elif recent_avg < older_avg * 0.9:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # Generate forecast if requested
    forecast = None
    if include_forecast:
        analyzer = FinancialAnalyzer()
        forecast = analyzer.forecast_cash_flow(historical[::-1])  # Reverse to chronological order
    
    return CashFlowResponse(
        current_period=CashFlowItem(
            period=current.period_label,
            operating=current.operating_cash_flow,
            investing=current.investing_cash_flow,
            financing=current.financing_cash_flow,
            net=current.net_cash_flow
        ),
        historical=historical,
        trend=trend,
        forecast=forecast
    )


@router.get("/expenses", response_model=ExpenseBreakdownResponse)
async def get_expense_breakdown(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get expense breakdown by category for the latest period.
    """
    result = await db.execute(
        select(FinancialMetrics)
        .where(FinancialMetrics.user_id == current_user.id)
        .order_by(desc(FinancialMetrics.period_end))
        .limit(2)
    )
    metrics_list = result.scalars().all()
    
    if not metrics_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No financial data found"
        )
    
    current = metrics_list[0]
    previous = metrics_list[1] if len(metrics_list) > 1 else None
    
    total = float(current.total_expenses)
    
    # Build categories (simplified - in production, would come from transaction data)
    categories = []
    
    if current.cost_of_goods_sold > 0:
        cogs_pct = float(current.cost_of_goods_sold / current.total_expenses * 100) if total > 0 else 0
        cogs_change = None
        if previous and previous.cost_of_goods_sold > 0:
            cogs_change = float((current.cost_of_goods_sold - previous.cost_of_goods_sold) / previous.cost_of_goods_sold * 100)
        categories.append(ExpenseCategory(
            category="Cost of Goods Sold",
            amount=current.cost_of_goods_sold,
            percentage=cogs_pct,
            change_from_previous=cogs_change
        ))
    
    if current.operating_expenses > 0:
        op_pct = float(current.operating_expenses / current.total_expenses * 100) if total > 0 else 0
        op_change = None
        if previous and previous.operating_expenses > 0:
            op_change = float((current.operating_expenses - previous.operating_expenses) / previous.operating_expenses * 100)
        categories.append(ExpenseCategory(
            category="Operating Expenses",
            amount=current.operating_expenses,
            percentage=op_pct,
            change_from_previous=op_change
        ))
    
    return ExpenseBreakdownResponse(
        total_expenses=current.total_expenses,
        period=current.period_label,
        categories=categories
    )
