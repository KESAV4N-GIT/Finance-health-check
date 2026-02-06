"""
Financial Schemas
Pydantic models for financial data and metrics.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class FinancialRatios(BaseModel):
    """Financial ratios calculated from metrics."""
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None


class MetricsResponse(BaseModel):
    """Response for financial metrics."""
    id: int
    period_label: str
    period_start: date
    period_end: date
    
    # Revenue & Income
    total_revenue: Decimal
    gross_profit: Decimal
    operating_income: Decimal
    net_profit: Decimal
    
    # Expenses
    total_expenses: Decimal
    cost_of_goods_sold: Decimal
    operating_expenses: Decimal
    
    # Ratios
    ratios: FinancialRatios
    
    class Config:
        from_attributes = True


class CashFlowItem(BaseModel):
    """Single cash flow data point."""
    period: str
    operating: Decimal
    investing: Decimal
    financing: Decimal
    net: Decimal


class CashFlowResponse(BaseModel):
    """Response for cash flow analysis."""
    current_period: CashFlowItem
    historical: List[CashFlowItem]
    trend: str  # increasing, decreasing, stable
    forecast: Optional[List[CashFlowItem]] = None


class ExpenseCategory(BaseModel):
    """Expense breakdown by category."""
    category: str
    amount: Decimal
    percentage: float
    change_from_previous: Optional[float] = None


class ExpenseBreakdownResponse(BaseModel):
    """Response for expense breakdown."""
    total_expenses: Decimal
    period: str
    categories: List[ExpenseCategory]


class FinancialSummary(BaseModel):
    """High-level financial summary for dashboard."""
    # Current period
    total_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal
    profit_margin: float
    
    # Cash position
    current_cash: Decimal
    operating_cash_flow: Decimal
    
    # Key ratios
    current_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    
    # Trends (percentage change from previous period)
    revenue_change: Optional[float] = None
    expense_change: Optional[float] = None
    profit_change: Optional[float] = None
    
    # Health indicators
    health_score: int = Field(..., ge=0, le=100)
    health_status: str  # healthy, caution, critical
    
    # Period info
    period_label: str
    last_updated: datetime


class TransactionCreate(BaseModel):
    """Schema for manual transaction entry."""
    date: date
    description: str = Field(..., max_length=500)
    amount: Decimal
    category: str = Field(..., max_length=100)
    transaction_type: str = Field(..., pattern="^(income|expense)$")
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None


class TransactionResponse(BaseModel):
    """Response for transaction."""
    id: int
    date: date
    description: str
    amount: Decimal
    category: str
    transaction_type: str
    payment_method: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
