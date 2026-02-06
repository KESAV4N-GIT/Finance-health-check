"""
Risk Assessment Engine
Calculates risk scores and creditworthiness.
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from app.models.financial_metrics import FinancialMetrics


class RiskAssessor:
    """Business risk assessment and credit scoring."""
    
    async def assess_risk(
        self,
        metrics: FinancialMetrics,
        historical_metrics: List[FinancialMetrics],
        industry: str
    ) -> dict:
        """
        Comprehensive risk assessment.
        
        Returns scores and identified risk factors.
        """
        # Calculate component scores
        liquidity_score = self._assess_liquidity_risk(metrics)
        solvency_score = self._assess_solvency_risk(metrics)
        operational_score = self._assess_operational_risk(metrics, historical_metrics)
        
        # Calculate overall score (weighted average)
        overall_score = int(
            liquidity_score * 0.35 +
            solvency_score * 0.35 +
            operational_score * 0.30
        )
        
        # Determine risk level
        if overall_score <= 30:
            risk_level = "low"
        elif overall_score <= 70:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            metrics, liquidity_score, solvency_score, operational_score
        )
        
        # Calculate creditworthiness
        creditworthiness_score = self._calculate_credit_score(metrics)
        
        return {
            "overall_score": overall_score,
            "liquidity_score": liquidity_score,
            "solvency_score": solvency_score,
            "operational_score": operational_score,
            "creditworthiness_score": creditworthiness_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors
        }
    
    def _assess_liquidity_risk(self, metrics: FinancialMetrics) -> int:
        """
        Assess liquidity risk (0-100, higher = more risk).
        """
        score = 50  # Base score
        
        # Current ratio assessment
        if metrics.current_ratio:
            cr = float(metrics.current_ratio)
            if cr >= 2.0:
                score -= 30
            elif cr >= 1.5:
                score -= 20
            elif cr >= 1.0:
                score -= 10
            elif cr >= 0.5:
                score += 20
            else:
                score += 40
        
        # Cash flow assessment
        if metrics.operating_cash_flow > 0:
            score -= 10
        else:
            score += 20
        
        return max(0, min(100, score))
    
    def _assess_solvency_risk(self, metrics: FinancialMetrics) -> int:
        """
        Assess solvency risk (0-100, higher = more risk).
        """
        score = 50
        
        # Debt to equity
        if metrics.debt_to_equity:
            dte = float(metrics.debt_to_equity)
            if dte <= 0.3:
                score -= 30
            elif dte <= 0.5:
                score -= 20
            elif dte <= 1.0:
                score -= 10
            elif dte <= 2.0:
                score += 15
            else:
                score += 35
        
        # Interest coverage (simplified)
        if metrics.operating_income > 0:
            score -= 10
        else:
            score += 20
        
        return max(0, min(100, score))
    
    def _assess_operational_risk(
        self,
        metrics: FinancialMetrics,
        historical: List[FinancialMetrics]
    ) -> int:
        """
        Assess operational risk based on trends (0-100).
        """
        score = 50
        
        # Revenue trend
        if len(historical) >= 3:
            revenues = [float(m.total_revenue) for m in historical[:3]]
            if all(revenues[i] >= revenues[i+1] for i in range(len(revenues)-1)):
                score -= 15  # Consistent growth
            elif all(revenues[i] <= revenues[i+1] for i in range(len(revenues)-1)):
                score += 20  # Declining revenue
        
        # Margin stability
        if metrics.net_margin:
            nm = float(metrics.net_margin)
            if nm >= 10:
                score -= 15
            elif nm >= 5:
                score -= 5
            elif nm >= 0:
                pass
            else:
                score += 25  # Operating at loss
        
        return max(0, min(100, score))
    
    def _identify_risk_factors(
        self,
        metrics: FinancialMetrics,
        liquidity_score: int,
        solvency_score: int,
        operational_score: int
    ) -> List[Dict[str, Any]]:
        """Identify specific risk factors."""
        factors = []
        
        # Liquidity risks
        if liquidity_score > 60:
            if metrics.current_ratio and float(metrics.current_ratio) < 1.0:
                factors.append({
                    "name": "Low Current Ratio",
                    "severity": "high" if float(metrics.current_ratio) < 0.5 else "medium",
                    "description": "Current assets may not cover short-term obligations",
                    "impact_area": "liquidity",
                    "recommendation": "Improve collection of receivables or negotiate longer payment terms"
                })
            
            if metrics.operating_cash_flow < 0:
                factors.append({
                    "name": "Negative Operating Cash Flow",
                    "severity": "critical",
                    "description": "Business operations are consuming cash",
                    "impact_area": "liquidity",
                    "recommendation": "Review operating costs and improve revenue collection"
                })
        
        # Solvency risks
        if solvency_score > 60:
            if metrics.debt_to_equity and float(metrics.debt_to_equity) > 2.0:
                factors.append({
                    "name": "High Debt Level",
                    "severity": "high",
                    "description": "Debt exceeds 2x equity, indicating high leverage",
                    "impact_area": "solvency",
                    "recommendation": "Consider debt restructuring or equity infusion"
                })
        
        # Profitability risks
        if metrics.net_margin and float(metrics.net_margin) < 0:
            factors.append({
                "name": "Operating Loss",
                "severity": "high",
                "description": "Business is currently unprofitable",
                "impact_area": "profitability",
                "recommendation": "Analyze cost structure and pricing strategy"
            })
        
        return factors
    
    def _calculate_credit_score(self, metrics: FinancialMetrics) -> int:
        """
        Calculate creditworthiness score (0-100).
        
        Based on: Revenue stability, profitability, debt level
        """
        score = 50
        
        # Revenue factor
        if metrics.total_revenue > 0:
            score += 15
        
        # Profitability factor
        if metrics.net_margin:
            nm = float(metrics.net_margin)
            if nm >= 15:
                score += 20
            elif nm >= 10:
                score += 15
            elif nm >= 5:
                score += 10
            elif nm >= 0:
                score += 5
        
        # Debt factor
        if metrics.debt_to_equity:
            dte = float(metrics.debt_to_equity)
            if dte <= 0.5:
                score += 15
            elif dte <= 1.0:
                score += 10
            elif dte <= 2.0:
                score += 5
            else:
                score -= 10
        
        return max(0, min(100, score))
    
    def calculate_creditworthiness(self, metrics: FinancialMetrics) -> dict:
        """Detailed creditworthiness breakdown."""
        overall_score = self._calculate_credit_score(metrics)
        
        # Determine grade
        if overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        elif overall_score >= 50:
            grade = "D"
        else:
            grade = "F"
        
        components = [
            {
                "component": "Revenue Stability",
                "score": min(100, 70 if metrics.total_revenue > 0 else 30),
                "weight": 0.3,
                "description": "Consistent revenue generation"
            },
            {
                "component": "Profitability",
                "score": min(100, 50 + int(float(metrics.net_margin or 0) * 3)),
                "weight": 0.35,
                "description": "Net profit margin"
            },
            {
                "component": "Debt Management",
                "score": min(100, 80 - int(float(metrics.debt_to_equity or 0) * 20)),
                "weight": 0.35,
                "description": "Debt to equity ratio"
            }
        ]
        
        positive_factors = []
        negative_factors = []
        
        if metrics.operating_cash_flow > 0:
            positive_factors.append("Positive operating cash flow")
        if metrics.current_ratio and float(metrics.current_ratio) >= 1.5:
            positive_factors.append("Healthy liquidity position")
        
        if metrics.debt_to_equity and float(metrics.debt_to_equity) > 1.5:
            negative_factors.append("High debt levels")
        if metrics.net_margin and float(metrics.net_margin) < 5:
            negative_factors.append("Low profit margins")
        
        return {
            "overall_score": overall_score,
            "grade": grade,
            "components": components,
            "positive_factors": positive_factors,
            "negative_factors": negative_factors,
            "improvement_suggestions": [
                "Maintain consistent revenue growth",
                "Reduce debt gradually",
                "Improve profit margins through cost optimization"
            ],
            "estimated_loan_amount": float(metrics.total_revenue) * 0.5 if metrics.total_revenue else None,
            "estimated_interest_rate": f"{12 - (overall_score // 20)}% - {14 - (overall_score // 20)}%"
        }
    
    def generate_forecast(
        self,
        historical_metrics: List[FinancialMetrics],
        forecast_type: str,
        horizon: str
    ) -> dict:
        """Generate financial forecast with scenarios."""
        periods = {"3_months": 3, "6_months": 6, "12_months": 12}.get(horizon, 6)
        
        # Get the metric to forecast
        if forecast_type == "revenue":
            values = [float(m.total_revenue) for m in historical_metrics]
        elif forecast_type == "expenses":
            values = [float(m.total_expenses) for m in historical_metrics]
        else:  # cash_flow
            values = [float(m.net_cash_flow) for m in historical_metrics]
        
        if not values:
            return {"error": "Insufficient data"}
        
        # Calculate growth rate
        avg_growth = sum(
            (values[i] - values[i-1]) / values[i-1] if values[i-1] != 0 else 0
            for i in range(1, len(values))
        ) / max(1, len(values) - 1)
        
        last_value = values[-1]
        
        expected_case = []
        best_case = []
        worst_case = []
        
        for i in range(periods):
            expected = last_value * (1 + avg_growth) ** (i + 1)
            best = last_value * (1 + avg_growth * 1.5) ** (i + 1)
            worst = last_value * (1 + avg_growth * 0.5) ** (i + 1)
            
            period_label = f"Month {i + 1}"
            
            expected_case.append({
                "period": period_label,
                "value": expected,
                "confidence_low": expected * 0.9,
                "confidence_high": expected * 1.1
            })
            best_case.append({
                "period": period_label,
                "value": best,
                "confidence_low": best * 0.95,
                "confidence_high": best * 1.05
            })
            worst_case.append({
                "period": period_label,
                "value": worst,
                "confidence_low": worst * 0.85,
                "confidence_high": worst * 0.95
            })
        
        trend = "growing" if avg_growth > 0.02 else "declining" if avg_growth < -0.02 else "stable"
        
        return {
            "forecast_type": forecast_type,
            "forecast_horizon": horizon,
            "expected_case": expected_case,
            "best_case": best_case,
            "worst_case": worst_case,
            "trend": trend,
            "growth_rate": avg_growth * 100,
            "key_assumptions": [
                "Based on historical growth patterns",
                "Assumes stable market conditions",
                "No major external shocks"
            ],
            "risks": [
                "Market volatility",
                "Seasonal fluctuations",
                "Economic changes"
            ]
        }
