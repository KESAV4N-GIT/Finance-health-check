"""
Financial Analysis Engine
Core financial calculations and metrics.
"""
from decimal import Decimal
from typing import List, Tuple, Optional
from app.models.financial_metrics import FinancialMetrics
from app.schemas.financial import CashFlowItem


class FinancialAnalyzer:
    """Core financial analysis calculations."""
    
    def calculate_health_score(self, metrics: FinancialMetrics) -> Tuple[int, str]:
        """
        Calculate overall financial health score (0-100).
        
        Returns (score, status) where status is 'healthy', 'caution', or 'critical'.
        """
        score = 50  # Base score
        
        # Liquidity (20 points)
        if metrics.current_ratio:
            cr = float(metrics.current_ratio)
            if cr >= 2.0:
                score += 20
            elif cr >= 1.5:
                score += 15
            elif cr >= 1.0:
                score += 10
            elif cr >= 0.5:
                score += 5
        
        # Profitability (25 points)
        if metrics.net_margin:
            nm = float(metrics.net_margin)
            if nm >= 15:
                score += 25
            elif nm >= 10:
                score += 20
            elif nm >= 5:
                score += 15
            elif nm >= 0:
                score += 10
            else:
                score -= 10  # Penalty for losses
        
        # Cash Flow (20 points)
        if metrics.operating_cash_flow > 0:
            score += 15
            if metrics.net_cash_flow > 0:
                score += 5
        
        # Debt (15 points)
        if metrics.debt_to_equity:
            dte = float(metrics.debt_to_equity)
            if dte <= 0.5:
                score += 15
            elif dte <= 1.0:
                score += 10
            elif dte <= 2.0:
                score += 5
            else:
                score -= 5  # Penalty for high debt
        
        # Normalize score to 0-100
        score = max(0, min(100, score))
        
        # Determine status
        if score >= 70:
            status = "healthy"
        elif score >= 40:
            status = "caution"
        else:
            status = "critical"
        
        return score, status
    
    def calculate_ratios(self, metrics: FinancialMetrics) -> dict:
        """Calculate all financial ratios."""
        ratios = {}
        
        # Liquidity Ratios
        if metrics.current_liabilities > 0:
            ratios["current_ratio"] = float(metrics.current_assets / metrics.current_liabilities)
            quick_assets = metrics.current_assets - metrics.inventory_value
            ratios["quick_ratio"] = float(quick_assets / metrics.current_liabilities)
        
        # Profitability Ratios
        if metrics.total_revenue > 0:
            ratios["gross_margin"] = float((metrics.gross_profit / metrics.total_revenue) * 100)
            ratios["operating_margin"] = float((metrics.operating_income / metrics.total_revenue) * 100)
            ratios["net_margin"] = float((metrics.net_profit / metrics.total_revenue) * 100)
        
        # Leverage Ratios
        if metrics.total_equity > 0:
            ratios["debt_to_equity"] = float(metrics.total_liabilities / metrics.total_equity)
            ratios["roe"] = float((metrics.net_profit / metrics.total_equity) * 100)
        
        if metrics.total_assets > 0:
            ratios["roa"] = float((metrics.net_profit / metrics.total_assets) * 100)
        
        return ratios
    
    def forecast_cash_flow(
        self,
        historical: List[CashFlowItem],
        periods: int = 6
    ) -> List[CashFlowItem]:
        """
        Generate cash flow forecast using moving average.
        
        Simple linear projection based on recent trends.
        """
        if len(historical) < 3:
            return []
        
        forecast = []
        
        # Calculate average changes
        net_values = [float(h.net) for h in historical]
        avg_change = sum(
            net_values[i] - net_values[i-1] 
            for i in range(1, len(net_values))
        ) / (len(net_values) - 1)
        
        last_value = net_values[-1]
        
        for i in range(periods):
            projected = last_value + (avg_change * (i + 1))
            forecast.append(CashFlowItem(
                period=f"M+{i+1}",
                operating=Decimal(str(projected * 0.8)),  # Estimate
                investing=Decimal(str(projected * -0.1)),
                financing=Decimal(str(projected * -0.1)),
                net=Decimal(str(projected))
            ))
        
        return forecast
    
    def calculate_working_capital_metrics(self, metrics: FinancialMetrics) -> dict:
        """Calculate working capital and cash conversion cycle metrics."""
        wc_metrics = {
            "working_capital": float(metrics.current_assets - metrics.current_liabilities),
            "working_capital_ratio": 0,
        }
        
        if metrics.current_liabilities > 0:
            wc_metrics["working_capital_ratio"] = float(
                metrics.current_assets / metrics.current_liabilities
            )
        
        # Days calculations (simplified)
        if metrics.total_revenue > 0:
            daily_revenue = float(metrics.total_revenue) / 365
            
            if daily_revenue > 0:
                wc_metrics["days_receivable"] = float(metrics.accounts_receivable) / daily_revenue
                wc_metrics["days_inventory"] = float(metrics.inventory_value) / daily_revenue
        
        if metrics.cost_of_goods_sold > 0:
            daily_cogs = float(metrics.cost_of_goods_sold) / 365
            if daily_cogs > 0:
                wc_metrics["days_payable"] = float(metrics.accounts_payable) / daily_cogs
        
        # Cash Conversion Cycle
        dso = wc_metrics.get("days_receivable", 0)
        dio = wc_metrics.get("days_inventory", 0)
        dpo = wc_metrics.get("days_payable", 0)
        wc_metrics["cash_conversion_cycle"] = dso + dio - dpo
        
        return wc_metrics
