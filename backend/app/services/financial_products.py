"""
Financial Products Recommendation Service
Recommend suitable financial products based on SME profile.
"""
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime


class FinancialProductsService:
    """Financial products recommendation engine."""
    
    def __init__(self):
        # Product database (simplified)
        self.products = {
            "loans": [
                {
                    "id": "wc_loan",
                    "name": "Working Capital Loan",
                    "provider_type": "bank",
                    "min_amount": 100000,
                    "max_amount": 10000000,
                    "interest_range": "10-15%",
                    "tenure": "12-36 months",
                    "requirements": ["2+ years in business", "Positive cash flow"],
                    "suitable_for": ["cash_flow_issues", "seasonal_business"]
                },
                {
                    "id": "term_loan",
                    "name": "Business Term Loan",
                    "provider_type": "bank",
                    "min_amount": 500000,
                    "max_amount": 50000000,
                    "interest_range": "9-14%",
                    "tenure": "3-7 years",
                    "requirements": ["3+ years in business", "Collateral"],
                    "suitable_for": ["expansion", "equipment_purchase"]
                },
                {
                    "id": "mudra_loan",
                    "name": "MUDRA Loan (Shishu/Kishore/Tarun)",
                    "provider_type": "government",
                    "min_amount": 0,
                    "max_amount": 1000000,
                    "interest_range": "8-12%",
                    "tenure": "12-60 months",
                    "requirements": ["MSME registration", "Business plan"],
                    "suitable_for": ["startup", "small_business", "micro_enterprise"]
                },
                {
                    "id": "invoice_financing",
                    "name": "Invoice Financing",
                    "provider_type": "nbfc",
                    "min_amount": 100000,
                    "max_amount": 5000000,
                    "interest_range": "12-18%",
                    "tenure": "30-90 days",
                    "requirements": ["B2B invoices", "Good debtor profile"],
                    "suitable_for": ["high_receivables", "cash_flow_issues"]
                }
            ],
            "insurance": [
                {
                    "id": "business_insurance",
                    "name": "Business Package Policy",
                    "coverage": ["Fire", "Theft", "Natural disasters"],
                    "premium_range": "0.1-0.5% of sum insured",
                    "suitable_for": ["all_businesses"]
                },
                {
                    "id": "liability_insurance",
                    "name": "Professional Liability Insurance",
                    "coverage": ["Professional errors", "Client claims"],
                    "premium_range": "0.3-1% of revenue",
                    "suitable_for": ["services", "consulting"]
                },
                {
                    "id": "keyman_insurance",
                    "name": "Key Person Insurance",
                    "coverage": ["Loss of key employee/owner"],
                    "premium_range": "Based on sum assured",
                    "suitable_for": ["owner_dependent", "small_team"]
                }
            ],
            "investments": [
                {
                    "id": "fd",
                    "name": "Business Fixed Deposit",
                    "return_range": "5-7%",
                    "liquidity": "Low",
                    "risk": "Very Low",
                    "suitable_for": ["cash_surplus", "reserve_building"]
                },
                {
                    "id": "liquid_fund",
                    "name": "Liquid Mutual Fund",
                    "return_range": "4-6%",
                    "liquidity": "High",
                    "risk": "Low",
                    "suitable_for": ["short_term_parking", "emergency_fund"]
                },
                {
                    "id": "debt_fund",
                    "name": "Short-term Debt Fund",
                    "return_range": "6-8%",
                    "liquidity": "Medium",
                    "risk": "Low-Medium",
                    "suitable_for": ["medium_term_surplus"]
                }
            ]
        }
    
    def recommend_products(
        self,
        business_profile: Dict[str, Any],
        financial_metrics: Dict[str, Any],
        needs: List[str] = None
    ) -> Dict[str, Any]:
        """
        Recommend financial products based on business profile and needs.
        """
        recommendations = {
            "loans": [],
            "insurance": [],
            "investments": [],
            "priority_actions": []
        }
        
        # Analyze needs
        needs = needs or self._infer_needs(financial_metrics)
        
        # Recommend loans
        recommendations["loans"] = self._recommend_loans(
            business_profile, financial_metrics, needs
        )
        
        # Recommend insurance
        recommendations["insurance"] = self._recommend_insurance(
            business_profile, financial_metrics
        )
        
        # Recommend investments
        recommendations["investments"] = self._recommend_investments(
            financial_metrics
        )
        
        # Priority actions
        recommendations["priority_actions"] = self._generate_priority_actions(
            financial_metrics, needs
        )
        
        return recommendations
    
    def _infer_needs(self, metrics: Dict) -> List[str]:
        """Infer business needs from financial metrics."""
        needs = []
        
        if metrics.get("current_ratio", 2) < 1.2:
            needs.append("liquidity")
        
        if metrics.get("cash_flow", 0) < 0:
            needs.append("cash_flow_issues")
        
        if metrics.get("receivable_days", 0) > 45:
            needs.append("high_receivables")
        
        if metrics.get("growth_rate", 0) > 20:
            needs.append("expansion")
        
        if metrics.get("debt_ratio", 0) < 0.3:
            needs.append("can_leverage")
        
        if metrics.get("cash_surplus", 0) > 0:
            needs.append("cash_surplus")
        
        return needs
    
    def _recommend_loans(
        self,
        profile: Dict,
        metrics: Dict,
        needs: List[str]
    ) -> List[Dict]:
        """Recommend suitable loan products."""
        recommendations = []
        revenue = metrics.get("annual_revenue", 0)
        
        for loan in self.products["loans"]:
            score = 0
            reasons = []
            
            # Check if suitable for needs
            for need in needs:
                if need in loan.get("suitable_for", []):
                    score += 30
                    reasons.append(f"Addresses {need.replace('_', ' ')}")
            
            # Check amount eligibility
            if loan["min_amount"] <= revenue * 0.3 <= loan["max_amount"]:
                score += 20
                reasons.append("Amount range suitable for your business size")
            
            # Check business age requirement
            business_age = profile.get("years_in_business", 1)
            if "2+ years" in str(loan.get("requirements")) and business_age < 2:
                score -= 30
                reasons.append("May not meet business age requirement")
            
            if score > 0:
                recommendations.append({
                    "product": loan,
                    "match_score": min(score, 100),
                    "reasons": reasons,
                    "estimated_eligible_amount": min(revenue * 0.3, loan["max_amount"])
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:3]
    
    def _recommend_insurance(
        self,
        profile: Dict,
        metrics: Dict
    ) -> List[Dict]:
        """Recommend insurance products."""
        recommendations = []
        industry = profile.get("industry", "general")
        
        for insurance in self.products["insurance"]:
            suitable = insurance.get("suitable_for", [])
            
            if "all_businesses" in suitable:
                recommendations.append({
                    "product": insurance,
                    "priority": "essential",
                    "reason": "Basic protection for all businesses"
                })
            elif industry in suitable:
                recommendations.append({
                    "product": insurance,
                    "priority": "recommended",
                    "reason": f"Relevant for {industry} industry"
                })
        
        return recommendations
    
    def _recommend_investments(self, metrics: Dict) -> List[Dict]:
        """Recommend investment products for surplus funds."""
        recommendations = []
        surplus = metrics.get("cash_surplus", 0)
        
        if surplus <= 0:
            return [{
                "message": "Focus on building cash reserves before investing",
                "target": "3-6 months of operating expenses"
            }]
        
        for investment in self.products["investments"]:
            recommendations.append({
                "product": investment,
                "suggested_allocation": self._calculate_allocation(surplus, investment)
            })
        
        return recommendations
    
    def _calculate_allocation(self, surplus: float, product: Dict) -> Dict:
        """Calculate suggested allocation for investment."""
        allocations = {
            "fd": 0.3,  # 30% in FD
            "liquid_fund": 0.5,  # 50% in liquid fund
            "debt_fund": 0.2  # 20% in debt fund
        }
        
        ratio = allocations.get(product["id"], 0.2)
        return {
            "percentage": ratio * 100,
            "amount": surplus * ratio
        }
    
    def _generate_priority_actions(
        self,
        metrics: Dict,
        needs: List[str]
    ) -> List[Dict]:
        """Generate priority financial actions."""
        actions = []
        
        if "liquidity" in needs:
            actions.append({
                "action": "Improve Liquidity",
                "priority": 1,
                "steps": [
                    "Accelerate receivables collection",
                    "Negotiate extended payment terms",
                    "Consider short-term financing"
                ]
            })
        
        if "cash_flow_issues" in needs:
            actions.append({
                "action": "Stabilize Cash Flow",
                "priority": 1,
                "steps": [
                    "Review and cut non-essential expenses",
                    "Explore invoice financing options",
                    "Build emergency reserve"
                ]
            })
        
        if metrics.get("insurance_coverage", False) is False:
            actions.append({
                "action": "Get Basic Insurance",
                "priority": 2,
                "steps": [
                    "Obtain business package policy",
                    "Consider key person insurance if applicable"
                ]
            })
        
        return actions
    
    def compare_products(
        self,
        product_ids: List[str],
        category: str = "loans"
    ) -> Dict[str, Any]:
        """
        Compare multiple products side by side.
        """
        products_list = self.products.get(category, [])
        selected = [p for p in products_list if p["id"] in product_ids]
        
        if len(selected) < 2:
            return {"error": "Need at least 2 products to compare"}
        
        comparison = {
            "products": selected,
            "comparison_matrix": self._build_comparison_matrix(selected, category)
        }
        
        return comparison
    
    def _build_comparison_matrix(
        self,
        products: List[Dict],
        category: str
    ) -> Dict:
        """Build comparison matrix for products."""
        if category == "loans":
            return {
                "interest_rate": {p["id"]: p["interest_range"] for p in products},
                "amount_range": {p["id"]: f"₹{p['min_amount']:,} - ₹{p['max_amount']:,}" for p in products},
                "tenure": {p["id"]: p["tenure"] for p in products}
            }
        return {}
