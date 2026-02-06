"""
Working Capital Optimization Service
Analyze and optimize working capital management.
"""
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime


class WorkingCapitalService:
    """Working capital analysis and optimization."""
    
    def __init__(self):
        # Industry benchmarks (simplified)
        self.benchmarks = {
            "retail": {"inventory_days": 45, "receivable_days": 15, "payable_days": 30},
            "manufacturing": {"inventory_days": 60, "receivable_days": 45, "payable_days": 45},
            "services": {"inventory_days": 0, "receivable_days": 30, "payable_days": 20},
            "technology": {"inventory_days": 30, "receivable_days": 45, "payable_days": 30},
            "default": {"inventory_days": 45, "receivable_days": 30, "payable_days": 30}
        }
    
    def analyze_working_capital(
        self,
        current_assets: Decimal,
        current_liabilities: Decimal,
        inventory: Decimal,
        receivables: Decimal,
        payables: Decimal,
        annual_revenue: Decimal,
        cogs: Decimal
    ) -> Dict[str, Any]:
        """
        Comprehensive working capital analysis.
        """
        # Calculate key metrics
        working_capital = current_assets - current_liabilities
        current_ratio = float(current_assets / current_liabilities) if current_liabilities > 0 else 0
        quick_ratio = float((current_assets - inventory) / current_liabilities) if current_liabilities > 0 else 0
        
        # Calculate days metrics
        daily_revenue = annual_revenue / 365
        daily_cogs = cogs / 365
        
        inventory_days = float(inventory / daily_cogs) if daily_cogs > 0 else 0
        receivable_days = float(receivables / daily_revenue) if daily_revenue > 0 else 0
        payable_days = float(payables / daily_cogs) if daily_cogs > 0 else 0
        
        # Cash conversion cycle
        cash_cycle = inventory_days + receivable_days - payable_days
        
        return {
            "working_capital": float(working_capital),
            "current_ratio": round(current_ratio, 2),
            "quick_ratio": round(quick_ratio, 2),
            "inventory_days": round(inventory_days, 1),
            "receivable_days": round(receivable_days, 1),
            "payable_days": round(payable_days, 1),
            "cash_conversion_cycle": round(cash_cycle, 1),
            "health_status": self._assess_health(current_ratio, cash_cycle),
            "optimization_potential": self._calculate_optimization_potential(
                inventory_days, receivable_days, payable_days, daily_revenue
            )
        }
    
    def _assess_health(self, current_ratio: float, cash_cycle: float) -> str:
        """Assess working capital health."""
        if current_ratio >= 1.5 and cash_cycle <= 30:
            return "excellent"
        elif current_ratio >= 1.2 and cash_cycle <= 60:
            return "good"
        elif current_ratio >= 1.0:
            return "adequate"
        else:
            return "needs_attention"
    
    def _calculate_optimization_potential(
        self,
        inv_days: float,
        rec_days: float,
        pay_days: float,
        daily_revenue: Decimal
    ) -> Dict[str, Any]:
        """Calculate potential cash release from optimization."""
        benchmarks = self.benchmarks["default"]
        
        inv_improvement = max(0, inv_days - benchmarks["inventory_days"])
        rec_improvement = max(0, rec_days - benchmarks["receivable_days"])
        pay_improvement = max(0, benchmarks["payable_days"] - pay_days)
        
        total_days = inv_improvement + rec_improvement + pay_improvement
        cash_release = float(daily_revenue * Decimal(str(total_days)))
        
        return {
            "days_reduction_potential": round(total_days, 1),
            "cash_release_potential": round(cash_release, 2),
            "areas": {
                "inventory": round(inv_improvement, 1),
                "receivables": round(rec_improvement, 1),
                "payables": round(pay_improvement, 1)
            }
        }
    
    def generate_recommendations(
        self,
        analysis: Dict[str, Any],
        industry: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations for working capital optimization.
        """
        recommendations = []
        benchmarks = self.benchmarks.get(industry, self.benchmarks["default"])
        
        # Inventory recommendations
        if analysis.get("inventory_days", 0) > benchmarks["inventory_days"]:
            recommendations.append({
                "area": "Inventory Management",
                "priority": "high",
                "current": f"{analysis['inventory_days']:.0f} days",
                "target": f"{benchmarks['inventory_days']} days",
                "actions": [
                    "Implement Just-In-Time (JIT) inventory management",
                    "Review slow-moving stock and consider clearance sales",
                    "Negotiate shorter lead times with suppliers",
                    "Use ABC analysis to prioritize inventory items"
                ],
                "potential_benefit": f"Release ₹{analysis['optimization_potential']['areas']['inventory'] * 1000:,.0f} in working capital"
            })
        
        # Receivables recommendations
        if analysis.get("receivable_days", 0) > benchmarks["receivable_days"]:
            recommendations.append({
                "area": "Accounts Receivable",
                "priority": "high",
                "current": f"{analysis['receivable_days']:.0f} days",
                "target": f"{benchmarks['receivable_days']} days",
                "actions": [
                    "Implement early payment discounts (e.g., 2/10 net 30)",
                    "Automate invoice reminders and follow-ups",
                    "Review credit policies for new customers",
                    "Consider invoice factoring for immediate cash"
                ],
                "potential_benefit": f"Release ₹{analysis['optimization_potential']['areas']['receivables'] * 1000:,.0f} in working capital"
            })
        
        # Payables recommendations
        if analysis.get("payable_days", 0) < benchmarks["payable_days"]:
            recommendations.append({
                "area": "Accounts Payable",
                "priority": "medium",
                "current": f"{analysis['payable_days']:.0f} days",
                "target": f"{benchmarks['payable_days']} days",
                "actions": [
                    "Negotiate longer payment terms with suppliers",
                    "Schedule payments strategically near due dates",
                    "Consolidate suppliers for better terms",
                    "Use credit lines strategically"
                ],
                "potential_benefit": f"Retain ₹{analysis['optimization_potential']['areas']['payables'] * 1000:,.0f} longer"
            })
        
        # Current ratio recommendations
        if analysis.get("current_ratio", 0) < 1.2:
            recommendations.append({
                "area": "Liquidity",
                "priority": "critical",
                "current": f"{analysis['current_ratio']:.2f}",
                "target": "1.5 or higher",
                "actions": [
                    "Build cash reserves through retained earnings",
                    "Consider short-term financing options",
                    "Reduce unnecessary current liabilities",
                    "Convert short-term debt to long-term"
                ]
            })
        
        return recommendations
    
    def calculate_financing_needs(
        self,
        projected_revenue_growth: float,
        current_working_capital: Decimal,
        cash_cycle: float
    ) -> Dict[str, Any]:
        """
        Calculate working capital financing needs for growth.
        """
        # Working capital typically needs to grow with revenue
        additional_wc_needed = float(current_working_capital) * (projected_revenue_growth / 100)
        
        # Financing options
        options = []
        
        if additional_wc_needed > 0:
            options = [
                {
                    "option": "Working Capital Loan",
                    "suitable_for": "Short-term needs",
                    "typical_rate": "10-15% p.a.",
                    "pros": ["Quick approval", "No collateral for small amounts"],
                    "cons": ["Higher interest rates"]
                },
                {
                    "option": "Overdraft Facility",
                    "suitable_for": "Fluctuating needs",
                    "typical_rate": "12-16% p.a.",
                    "pros": ["Flexible", "Pay interest only on used amount"],
                    "cons": ["Needs good banking relationship"]
                },
                {
                    "option": "Invoice Discounting",
                    "suitable_for": "High receivables",
                    "typical_rate": "12-18% p.a.",
                    "pros": ["Converts receivables to cash", "Off-balance sheet"],
                    "cons": ["Customer may know about factoring"]
                },
                {
                    "option": "Channel Finance",
                    "suitable_for": "Supply chain needs",
                    "typical_rate": "9-12% p.a.",
                    "pros": ["Lower rates", "Strengthens supplier relationships"],
                    "cons": ["Limited to specific supply chains"]
                }
            ]
        
        return {
            "projected_growth": projected_revenue_growth,
            "additional_wc_needed": round(additional_wc_needed, 2),
            "current_cash_cycle": cash_cycle,
            "financing_options": options,
            "recommendation": self._financing_recommendation(additional_wc_needed, cash_cycle)
        }
    
    def _financing_recommendation(self, amount_needed: float, cash_cycle: float) -> str:
        """Generate financing recommendation."""
        if amount_needed <= 0:
            return "No additional financing needed. Consider investing surplus in growth."
        elif cash_cycle > 60:
            return "Consider invoice discounting to reduce cash cycle before taking loans."
        elif amount_needed < 500000:
            return "Working capital loan or overdraft facility would be suitable."
        else:
            return "Explore multiple options including channel finance for larger needs."
