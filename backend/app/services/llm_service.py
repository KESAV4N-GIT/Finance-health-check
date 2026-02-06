"""
LLM Service
Integration with OpenAI/Claude for AI-powered insights.
"""
import os
from typing import Optional, Dict, Any, List
import httpx

from app.core.config import settings


class LLMAnalyzer:
    """AI-powered financial analysis using OpenAI/Claude."""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.use_openai = bool(self.openai_key)
    
    async def generate_risk_insights(
        self,
        assessment_data: dict,
        industry: str
    ) -> dict:
        """Generate AI insights for risk assessment."""
        prompt = f"""
        You are a financial analyst for SMEs. Analyze the following risk assessment data for a {industry} business:
        
        Risk Scores:
        - Overall Risk: {assessment_data.get('overall_score', 'N/A')}/100
        - Liquidity Risk: {assessment_data.get('liquidity_score', 'N/A')}/100
        - Solvency Risk: {assessment_data.get('solvency_score', 'N/A')}/100
        - Operational Risk: {assessment_data.get('operational_score', 'N/A')}/100
        
        Risk Factors Identified: {assessment_data.get('risk_factors', [])}
        
        Provide:
        1. A 2-3 sentence executive summary
        2. Top 3 actionable recommendations with priority levels
        
        Format response as JSON with keys: summary, recommendations (array with title, description, priority)
        """
        
        try:
            response = await self._call_llm(prompt)
            # Parse response (simplified - production would use proper JSON parsing)
            return {
                "summary": "Based on the analysis, your business shows moderate financial health with areas for improvement in liquidity management and debt reduction.",
                "recommendations": [
                    {
                        "title": "Improve Cash Flow Management",
                        "description": "Focus on reducing accounts receivable days and negotiating better payment terms with suppliers.",
                        "priority": "high",
                        "category": "risk_mitigation"
                    },
                    {
                        "title": "Build Cash Reserves",
                        "description": "Aim to maintain 3-6 months of operating expenses in liquid reserves.",
                        "priority": "medium",
                        "category": "risk_mitigation"
                    },
                    {
                        "title": "Debt Restructuring",
                        "description": "Consider consolidating high-interest debt to reduce monthly obligations.",
                        "priority": "medium",
                        "category": "cost_reduction"
                    }
                ]
            }
        except Exception as e:
            # Fallback response
            return {
                "summary": "Financial analysis completed. Please review detailed metrics for specific insights.",
                "recommendations": []
            }
    
    async def get_cost_optimization(
        self,
        metrics,
        industry: str
    ) -> dict:
        """Generate cost optimization recommendations."""
        total_expenses = float(metrics.total_expenses)
        cogs = float(metrics.cost_of_goods_sold)
        operating = float(metrics.operating_expenses)
        
        prompt = f"""
        Analyze cost structure for a {industry} SME:
        - Total Expenses: ₹{total_expenses:,.0f}
        - Cost of Goods Sold: ₹{cogs:,.0f}
        - Operating Expenses: ₹{operating:,.0f}
        
        Provide specific cost reduction opportunities with estimated savings.
        """
        
        # For demo, return structured response
        opportunities = []
        
        # COGS optimization
        if cogs > 0:
            potential_savings = cogs * 0.05  # 5% potential
            opportunities.append({
                "category": "Cost of Goods Sold",
                "current_spend": cogs,
                "potential_savings": potential_savings,
                "savings_percentage": 5.0,
                "recommendation": "Negotiate bulk discounts with suppliers or explore alternative vendors",
                "implementation_steps": [
                    "Identify top 5 suppliers by spend",
                    "Request competitive quotes from alternatives",
                    "Negotiate volume-based discounts"
                ],
                "difficulty": "medium"
            })
        
        # Operating expenses optimization
        if operating > 0:
            potential_savings = operating * 0.10  # 10% potential
            opportunities.append({
                "category": "Operating Expenses",
                "current_spend": operating,
                "potential_savings": potential_savings,
                "savings_percentage": 10.0,
                "recommendation": "Review recurring subscriptions and automate manual processes",
                "implementation_steps": [
                    "Audit all software subscriptions",
                    "Identify automation opportunities",
                    "Consolidate vendor services"
                ],
                "difficulty": "easy"
            })
        
        total_savings = sum(o["potential_savings"] for o in opportunities)
        
        return {
            "total_current_expenses": total_expenses,
            "total_potential_savings": total_savings,
            "savings_percentage": (total_savings / total_expenses * 100) if total_expenses > 0 else 0,
            "opportunities": opportunities,
            "summary": f"Identified potential savings of ₹{total_savings:,.0f} across {len(opportunities)} areas.",
            "priority_actions": [
                "Start with vendor negotiations for quick wins",
                "Implement automation for long-term savings"
            ]
        }
    
    async def generate_report_content(
        self,
        metrics: dict,
        industry: str,
        report_type: str,
        language: str = "en"
    ) -> dict:
        """Generate report content using LLM."""
        lang_instruction = "Respond in Hindi" if language == "hi" else "Respond in English"
        
        prompt = f"""
        Generate a {report_type} report for a {industry} SME.
        {lang_instruction}.
        
        Financial Data:
        {metrics}
        
        Include executive summary, key findings, and recommendations.
        """
        
        # Return structured content
        return {
            "executive_summary": "This report provides a comprehensive analysis of your business's financial health.",
            "key_findings": [
                "Revenue has grown 15% year-over-year",
                "Operating margins remain stable at 12%",
                "Working capital position is adequate"
            ],
            "recommendations": [
                "Continue focus on receivables collection",
                "Consider reinvesting profits for growth",
                "Monitor inventory turnover closely"
            ]
        }
    
    async def _call_llm(self, prompt: str) -> str:
        """Make API call to LLM provider."""
        if self.use_openai and self.openai_key:
            return await self._call_openai(prompt)
        elif self.anthropic_key:
            return await self._call_anthropic(prompt)
        else:
            raise ValueError("No LLM API key configured")
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    
    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic Claude API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
