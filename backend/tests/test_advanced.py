"""
Advanced Features API Tests
"""
import pytest
from httpx import AsyncClient


class TestBookkeepingEndpoints:
    """Test bookkeeping API endpoints."""
    
    @pytest.mark.asyncio
    async def test_categorize_transaction(self, client: AsyncClient, auth_headers):
        """Test transaction categorization."""
        response = await client.post(
            "/api/advanced/bookkeeping/categorize",
            json={"description": "Office rent payment", "amount": -50000},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_type"] == "expense"
        assert data["category"] == "rent"
    
    @pytest.mark.asyncio
    async def test_batch_categorize(self, client: AsyncClient, auth_headers):
        """Test batch transaction categorization."""
        response = await client.post(
            "/api/advanced/bookkeeping/batch-categorize",
            json={
                "transactions": [
                    {"description": "Salary payment", "amount": -100000},
                    {"description": "Product sale", "amount": 150000}
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["categorized"]) == 2


class TestTaxComplianceEndpoints:
    """Test tax compliance API endpoints."""
    
    @pytest.mark.asyncio
    async def test_validate_gstin(self, client: AsyncClient, auth_headers):
        """Test GSTIN validation."""
        response = await client.post(
            "/api/advanced/tax/validate-gstin",
            json={"gstin": "27AAPFU0939F1ZV"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_valid" in data
        assert "state_code" in data
    
    @pytest.mark.asyncio
    async def test_calculate_gst(self, client: AsyncClient, auth_headers):
        """Test GST calculation."""
        response = await client.post(
            "/api/advanced/tax/calculate-gst",
            json={"amount": 10000, "rate": 18, "is_interstate": False},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_gst"] == 1800
        assert data["cgst"] == 900
        assert data["sgst"] == 900
    
    @pytest.mark.asyncio
    async def test_compliance_checklist(self, client: AsyncClient, auth_headers):
        """Test compliance checklist."""
        response = await client.get(
            "/api/advanced/tax/compliance-checklist/01-2026",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "checklist" in data


class TestForecastingEndpoints:
    """Test forecasting API endpoints."""
    
    @pytest.mark.asyncio
    async def test_forecast_cash_flow(self, client: AsyncClient, auth_headers):
        """Test cash flow forecast."""
        response = await client.post(
            "/api/advanced/forecast/cash-flow",
            json={
                "historical_data": [
                    {"period": "2025-09", "revenue": 100000, "expenses": 80000},
                    {"period": "2025-10", "revenue": 110000, "expenses": 85000},
                    {"period": "2025-11", "revenue": 120000, "expenses": 90000},
                ],
                "months_ahead": 3
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
    
    @pytest.mark.asyncio
    async def test_scenario_analysis(self, client: AsyncClient, auth_headers):
        """Test scenario analysis."""
        response = await client.post(
            "/api/advanced/forecast/scenarios",
            params={"base_revenue": 1000000, "base_expenses": 800000},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data


class TestWorkingCapitalEndpoints:
    """Test working capital API endpoints."""
    
    @pytest.mark.asyncio
    async def test_analyze_working_capital(self, client: AsyncClient, auth_headers):
        """Test working capital analysis."""
        response = await client.post(
            "/api/advanced/working-capital/analyze",
            json={
                "current_assets": 500000,
                "current_liabilities": 300000,
                "inventory": 100000,
                "receivables": 150000,
                "payables": 100000,
                "annual_revenue": 1200000,
                "cogs": 800000,
                "industry": "retail"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "recommendations" in data


class TestProductRecommendationEndpoints:
    """Test product recommendation API endpoints."""
    
    @pytest.mark.asyncio
    async def test_recommend_products(self, client: AsyncClient, auth_headers):
        """Test product recommendations."""
        response = await client.post(
            "/api/advanced/products/recommend",
            json={
                "years_in_business": 3,
                "industry": "retail",
                "annual_revenue": 1000000,
                "current_ratio": 1.5,
                "cash_flow": 50000,
                "receivable_days": 30,
                "growth_rate": 10,
                "cash_surplus": 100000
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "loans" in data
        assert "insurance" in data
