"""
Financial Metrics Model
Stores calculated financial metrics for analysis periods.
"""
from datetime import datetime, date
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, DateTime, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FinancialMetrics(Base):
    """Stores calculated financial metrics for a specific period."""
    
    __tablename__ = "financial_metrics"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    
    # Period
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    period_label: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Q1 2026", "Jan 2026"
    
    # Revenue & Income (encrypted columns recommended for production)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    gross_profit: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    operating_income: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    net_profit: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Expenses
    total_expenses: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    cost_of_goods_sold: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    operating_expenses: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Cash Flow
    operating_cash_flow: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    investing_cash_flow: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    financing_cash_flow: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    net_cash_flow: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Balance Sheet Items
    accounts_receivable: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    accounts_payable: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    inventory_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    current_assets: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    current_liabilities: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    total_assets: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    total_liabilities: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    total_equity: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Debt
    short_term_debt: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    long_term_debt: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=0, nullable=False)
    
    # Calculated Ratios (stored for quick access)
    current_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    quick_ratio: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    gross_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    operating_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    net_margin: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    debt_to_equity: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    roe: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    roa: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 4), nullable=True)
    
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
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="financial_metrics")
    
    def __repr__(self) -> str:
        return f"<FinancialMetrics(id={self.id}, period={self.period_label}, revenue={self.total_revenue})>"
