"""
Financial Forecasting Service
Cash flow forecasting and financial projections.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import statistics


class ForecastingService:
    """Financial forecasting and projections."""
    
    def __init__(self):
        self.default_forecast_months = 6
    
    def forecast_cash_flow(
        self,
        historical_data: List[Dict],
        months_ahead: int = 6
    ) -> Dict[str, Any]:
        """
        Forecast future cash flows based on historical data.
        Uses weighted moving average for trends.
        """
        if not historical_data or len(historical_data) < 3:
            return {
                "error": "Insufficient historical data. Need at least 3 months.",
                "forecast": [],
                "confidence": 0
            }
        
        # Extract revenue and expense series
        revenues = [Decimal(str(d.get('revenue', 0))) for d in historical_data]
        expenses = [Decimal(str(d.get('expenses', 0))) for d in historical_data]
        
        # Calculate weighted moving average (recent months weighted more)
        revenue_forecast = self._weighted_forecast(revenues, months_ahead)
        expense_forecast = self._weighted_forecast(expenses, months_ahead)
        
        # Generate forecast periods
        last_period = historical_data[-1].get('period', datetime.now().strftime('%Y-%m'))
        forecast_periods = self._generate_periods(last_period, months_ahead)
        
        forecast = []
        cumulative_net = Decimal('0')
        
        for i in range(months_ahead):
            net = revenue_forecast[i] - expense_forecast[i]
            cumulative_net += net
            
            forecast.append({
                "period": forecast_periods[i],
                "projected_revenue": float(revenue_forecast[i]),
                "projected_expenses": float(expense_forecast[i]),
                "projected_net_cash_flow": float(net),
                "cumulative_net_cash_flow": float(cumulative_net),
                "confidence": self._calculate_confidence(i)
            })
        
        # Calculate trends
        revenue_trend = self._calculate_trend(revenues)
        expense_trend = self._calculate_trend(expenses)
        
        return {
            "forecast": forecast,
            "summary": {
                "average_monthly_revenue": float(sum(revenue_forecast) / len(revenue_forecast)),
                "average_monthly_expenses": float(sum(expense_forecast) / len(expense_forecast)),
                "average_monthly_net": float(sum(r - e for r, e in zip(revenue_forecast, expense_forecast)) / months_ahead),
                "revenue_trend": revenue_trend,
                "expense_trend": expense_trend,
                "overall_confidence": 75
            },
            "risks": self._identify_forecast_risks(revenue_forecast, expense_forecast),
            "assumptions": [
                "Based on historical trends continuing",
                "No major market changes assumed",
                "Seasonality patterns maintained"
            ]
        }
    
    def _weighted_forecast(
        self,
        data: List[Decimal],
        periods: int
    ) -> List[Decimal]:
        """Calculate weighted moving average forecast."""
        # Use last 6 months or all available
        recent = data[-6:] if len(data) >= 6 else data
        
        # Assign weights (more recent = higher weight)
        weights = list(range(1, len(recent) + 1))
        total_weight = sum(weights)
        
        weighted_avg = sum(
            val * weight for val, weight in zip(recent, weights)
        ) / total_weight
        
        # Calculate growth rate
        if len(recent) >= 2:
            growth_rate = (recent[-1] - recent[0]) / (len(recent) - 1) / recent[0] if recent[0] != 0 else Decimal('0')
        else:
            growth_rate = Decimal('0')
        
        # Cap growth rate to reasonable bounds
        growth_rate = max(min(growth_rate, Decimal('0.1')), Decimal('-0.1'))
        
        forecast = []
        current_value = weighted_avg
        
        for i in range(periods):
            current_value = current_value * (1 + growth_rate * Decimal('0.5'))  # Dampen growth
            forecast.append(round(current_value, 2))
        
        return forecast
    
    def _generate_periods(self, last_period: str, months: int) -> List[str]:
        """Generate future period labels."""
        try:
            year, month = map(int, last_period.split('-'))
        except:
            year, month = datetime.now().year, datetime.now().month
        
        periods = []
        for _ in range(months):
            month += 1
            if month > 12:
                month = 1
                year += 1
            periods.append(f"{year}-{month:02d}")
        
        return periods
    
    def _calculate_confidence(self, month_index: int) -> int:
        """Confidence decreases for further out forecasts."""
        base_confidence = 85
        decay_per_month = 5
        return max(50, base_confidence - (month_index * decay_per_month))
    
    def _calculate_trend(self, data: List[Decimal]) -> str:
        """Determine trend direction."""
        if len(data) < 2:
            return "stable"
        
        first_half = sum(data[:len(data)//2]) / (len(data)//2)
        second_half = sum(data[len(data)//2:]) / (len(data) - len(data)//2)
        
        change = (second_half - first_half) / first_half if first_half != 0 else 0
        
        if change > Decimal('0.05'):
            return "increasing"
        elif change < Decimal('-0.05'):
            return "decreasing"
        return "stable"
    
    def _identify_forecast_risks(
        self,
        revenue_forecast: List[Decimal],
        expense_forecast: List[Decimal]
    ) -> List[Dict]:
        """Identify potential risks in forecast."""
        risks = []
        
        # Check for negative cash flow months
        for i, (rev, exp) in enumerate(zip(revenue_forecast, expense_forecast)):
            if exp > rev:
                risks.append({
                    "type": "negative_cash_flow",
                    "month": i + 1,
                    "severity": "high" if exp > rev * Decimal('1.2') else "medium",
                    "description": f"Projected expenses exceed revenue in month {i + 1}"
                })
        
        # Check for declining revenue
        if len(revenue_forecast) >= 3:
            if all(revenue_forecast[i] > revenue_forecast[i+1] for i in range(min(3, len(revenue_forecast)-1))):
                risks.append({
                    "type": "declining_revenue",
                    "severity": "high",
                    "description": "Revenue shows consistent decline over forecast period"
                })
        
        return risks
    
    def project_break_even(
        self,
        fixed_costs: Decimal,
        variable_cost_ratio: Decimal,
        current_revenue: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate break-even point and time to achieve it.
        """
        if variable_cost_ratio >= 1:
            return {"error": "Variable cost ratio cannot be 100% or more"}
        
        # Break-even revenue = Fixed Costs / (1 - Variable Cost Ratio)
        contribution_margin = 1 - float(variable_cost_ratio)
        break_even_revenue = float(fixed_costs) / contribution_margin
        
        # Calculate gap
        gap = break_even_revenue - float(current_revenue)
        
        return {
            "break_even_revenue": round(break_even_revenue, 2),
            "current_revenue": float(current_revenue),
            "gap": round(gap, 2),
            "contribution_margin": round(contribution_margin * 100, 1),
            "is_profitable": gap <= 0,
            "revenue_increase_needed": round(gap / float(current_revenue) * 100, 1) if current_revenue > 0 else None,
            "recommendations": self._break_even_recommendations(gap, fixed_costs, variable_cost_ratio)
        }
    
    def _break_even_recommendations(
        self,
        gap: float,
        fixed_costs: Decimal,
        variable_ratio: Decimal
    ) -> List[str]:
        """Generate recommendations based on break-even analysis."""
        recs = []
        
        if gap > 0:
            recs.append(f"Increase revenue by ₹{gap:,.0f} to reach break-even")
            recs.append(f"Or reduce fixed costs by ₹{gap * (1 - float(variable_ratio)):,.0f}")
            recs.append("Consider pricing optimization to improve margins")
        else:
            recs.append("Currently operating above break-even")
            recs.append("Focus on scaling profitable products/services")
        
        return recs
    
    def scenario_analysis(
        self,
        base_revenue: Decimal,
        base_expenses: Decimal,
        scenarios: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform scenario analysis (best, worst, most likely).
        """
        scenarios = scenarios or ["optimistic", "base", "pessimistic"]
        
        results = {}
        
        # Define scenario adjustments
        adjustments = {
            "optimistic": {"revenue": 1.20, "expenses": 0.95},
            "base": {"revenue": 1.0, "expenses": 1.0},
            "pessimistic": {"revenue": 0.80, "expenses": 1.10}
        }
        
        for scenario in scenarios:
            adj = adjustments.get(scenario, adjustments["base"])
            
            proj_revenue = base_revenue * Decimal(str(adj["revenue"]))
            proj_expenses = base_expenses * Decimal(str(adj["expenses"]))
            net = proj_revenue - proj_expenses
            margin = (net / proj_revenue * 100) if proj_revenue > 0 else 0
            
            results[scenario] = {
                "revenue": float(proj_revenue),
                "expenses": float(proj_expenses),
                "net_profit": float(net),
                "profit_margin": float(margin),
                "is_profitable": net > 0
            }
        
        return {
            "scenarios": results,
            "recommendation": self._scenario_recommendation(results)
        }
    
    def _scenario_recommendation(self, results: Dict) -> str:
        """Generate recommendation based on scenario analysis."""
        if results.get("pessimistic", {}).get("is_profitable", False):
            return "Strong position - profitable even in worst case"
        elif results.get("base", {}).get("is_profitable", False):
            return "Good position - profitable in base case. Build reserves for downturns."
        else:
            return "Action needed - not profitable in base case. Focus on cost reduction or revenue growth."
