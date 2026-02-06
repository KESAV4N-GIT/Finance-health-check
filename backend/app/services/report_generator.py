"""
Report Generator Service
Generates and exports financial reports.
"""
import os
from datetime import datetime
from typing import Optional
from app.models.report import Report, ReportType, ReportStatus
from app.services.llm_service import LLMAnalyzer


class ReportGenerator:
    """Generates financial reports with AI assistance."""
    
    def __init__(self):
        self.llm = LLMAnalyzer()
    
    async def generate_report_async(
        self,
        report_id: int,
        user_id: int,
        report_type: ReportType,
        language: str,
        include_forecast: bool
    ):
        """
        Background task to generate report.
        
        Updates report status and content in database.
        """
        # This would be implemented with database access in production
        # For now, placeholder implementation
        pass
    
    async def generate_financial_health_report(
        self,
        metrics: dict,
        industry: str,
        language: str
    ) -> dict:
        """Generate comprehensive financial health report."""
        content = await self.llm.generate_report_content(
            metrics, industry, "financial_health", language
        )
        
        return {
            "financial_overview": {
                "revenue": metrics.get("total_revenue", 0),
                "expenses": metrics.get("total_expenses", 0),
                "net_profit": metrics.get("net_profit", 0),
                "cash_flow": metrics.get("operating_cash_flow", 0)
            },
            "key_metrics": {
                "current_ratio": metrics.get("current_ratio"),
                "debt_to_equity": metrics.get("debt_to_equity"),
                "gross_margin": metrics.get("gross_margin"),
                "net_margin": metrics.get("net_margin")
            },
            "analysis": content,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def generate_investor_report(
        self,
        metrics: dict,
        risk_data: dict,
        industry: str,
        language: str
    ) -> dict:
        """Generate investor-ready report."""
        return {
            "company_overview": {
                "industry": industry,
                "assessment_date": datetime.utcnow().isoformat()
            },
            "financial_highlights": {
                "revenue": metrics.get("total_revenue", 0),
                "growth_rate": metrics.get("revenue_growth", 0),
                "profit_margin": metrics.get("net_margin", 0)
            },
            "risk_profile": {
                "overall_score": risk_data.get("overall_score", 50),
                "creditworthiness": risk_data.get("creditworthiness_score", 50),
                "risk_level": risk_data.get("risk_level", "medium")
            },
            "investment_highlights": [
                "Stable revenue growth",
                "Strong market position",
                "Experienced management team"
            ],
            "risk_factors": risk_data.get("risk_factors", [])
        }
    
    async def export_report(self, report: Report, format: str) -> str:
        """
        Export report to specified format.
        
        Returns path to exported file.
        """
        export_dir = "./exports"
        os.makedirs(export_dir, exist_ok=True)
        
        filename = f"{report.id}_{report.report_type.value}_{datetime.utcnow().strftime('%Y%m%d')}.{format}"
        export_path = os.path.join(export_dir, filename)
        
        if format == "pdf":
            await self._export_pdf(report, export_path)
        elif format == "xlsx":
            await self._export_excel(report, export_path)
        elif format == "html":
            await self._export_html(report, export_path)
        
        return export_path
    
    async def _export_pdf(self, report: Report, path: str):
        """Export report as PDF."""
        # In production, use reportlab or weasyprint
        # Placeholder: create simple text file
        with open(path, "w") as f:
            f.write(f"Report: {report.title}\n")
            f.write(f"Type: {report.report_type.value}\n")
            f.write(f"Generated: {report.generated_at}\n")
    
    async def _export_excel(self, report: Report, path: str):
        """Export report as Excel."""
        import pandas as pd
        
        # Create DataFrame from report content
        if report.content:
            df = pd.DataFrame([report.content.get("key_metrics", {})])
            df.to_excel(path, index=False)
    
    async def _export_html(self, report: Report, path: str):
        """Export report as HTML."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .summary {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>{report.title}</h1>
            <p>Generated: {report.generated_at}</p>
            <div class="summary">
                {report.summary or "No summary available"}
            </div>
        </body>
        </html>
        """
        
        with open(path, "w") as f:
            f.write(html_content)
