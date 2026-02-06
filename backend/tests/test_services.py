"""
Service Unit Tests
Tests for business logic services.
"""
import pytest
from decimal import Decimal
from datetime import date

from app.services.bookkeeping import BookkeepingService
from app.services.tax_compliance import TaxComplianceService, GSTSlabRate
from app.services.forecasting import ForecastingService
from app.services.working_capital import WorkingCapitalService
from app.services.financial_products import FinancialProductsService


class TestBookkeepingService:
    """Tests for BookkeepingService."""
    
    def setup_method(self):
        self.service = BookkeepingService()
    
    def test_categorize_expense_rent(self):
        """Test categorizing rent expense."""
        result = self.service.categorize_transaction(
            "Monthly office rent payment",
            Decimal("-50000")
        )
        assert result["transaction_type"] == "expense"
        assert result["category"] == "rent"
        assert result["confidence"] >= 0.5
    
    def test_categorize_expense_salary(self):
        """Test categorizing salary expense."""
        result = self.service.categorize_transaction(
            "Employee salary for January",
            Decimal("-100000")
        )
        assert result["transaction_type"] == "expense"
        assert result["category"] == "salary"
    
    def test_categorize_income_sale(self):
        """Test categorizing sales income."""
        result = self.service.categorize_transaction(
            "Product sale invoice #1234",
            Decimal("150000")
        )
        assert result["transaction_type"] == "income"
        assert result["category"] == "product_sales"
    
    def test_batch_categorize(self):
        """Test batch categorization."""
        transactions = [
            {"description": "Rent payment", "amount": -30000},
            {"description": "Customer payment", "amount": 50000},
        ]
        results = self.service.batch_categorize(transactions)
        assert len(results) == 2
        assert results[0]["category"] == "rent"
    
    def test_generate_journal_entry_expense(self):
        """Test journal entry generation for expense."""
        result = self.service.generate_journal_entry(
            "expense",
            Decimal("10000"),
            "Office supplies purchase",
            "supplies"
        )
        assert result["is_balanced"] is True
        assert len(result["entries"]) == 2
        assert result["total_debit"] == result["total_credit"]
    
    def test_reconcile_accounts_balanced(self):
        """Test bank reconciliation when balanced."""
        result = self.service.reconcile_accounts(
            book_balance=Decimal("100000"),
            bank_balance=Decimal("100000"),
            uncleared_transactions=[]
        )
        assert result["is_reconciled"] is True
        assert result["difference"] == 0


class TestTaxComplianceService:
    """Tests for TaxComplianceService."""
    
    def setup_method(self):
        self.service = TaxComplianceService()
    
    def test_validate_gstin_valid(self):
        """Test GSTIN validation with valid format."""
        result = self.service.validate_gstin("27AAPFU0939F1ZV")
        # Format is valid
        assert "gstin" in result
        assert result["state_code"] == "27"
    
    def test_validate_gstin_invalid_length(self):
        """Test GSTIN validation with invalid length."""
        result = self.service.validate_gstin("27AAPFU0939F1Z")
        assert result["is_valid"] is False
        assert any("15 characters" in e for e in result["errors"])
    
    def test_calculate_gst_intrastate(self):
        """Test GST calculation for intrastate transaction."""
        result = self.service.calculate_gst(
            Decimal("10000"),
            GSTSlabRate.EIGHTEEN,
            is_interstate=False
        )
        assert result["cgst"] == result["sgst"]
        assert result["igst"] == 0
        assert result["total_gst"] == 1800
        assert result["total_amount"] == 11800
    
    def test_calculate_gst_interstate(self):
        """Test GST calculation for interstate transaction."""
        result = self.service.calculate_gst(
            Decimal("10000"),
            GSTSlabRate.EIGHTEEN,
            is_interstate=True
        )
        assert result["igst"] == 1800
        assert result["cgst"] == 0
        assert result["sgst"] == 0
    
    def test_calculate_tds(self):
        """Test TDS calculation."""
        result = self.service.calculate_tds(
            Decimal("100000"),
            "professional_fees",
            is_pan_available=True
        )
        assert result["tds_rate"] == 10
        assert result["tds_amount"] == 10000
        assert result["net_payable"] == 90000
    
    def test_compliance_checklist(self):
        """Test compliance checklist generation."""
        result = self.service.generate_compliance_checklist("01-2026")
        assert len(result) >= 4
        assert any(item["item"] == "GSTR-1 Filing" for item in result)


class TestForecastingService:
    """Tests for ForecastingService."""
    
    def setup_method(self):
        self.service = ForecastingService()
    
    def test_forecast_cash_flow_insufficient_data(self):
        """Test forecasting with insufficient data."""
        result = self.service.forecast_cash_flow([{"revenue": 100000, "expenses": 80000}], 6)
        assert "error" in result
    
    def test_forecast_cash_flow_success(self):
        """Test successful cash flow forecast."""
        historical = [
            {"period": "2025-09", "revenue": 100000, "expenses": 80000},
            {"period": "2025-10", "revenue": 110000, "expenses": 85000},
            {"period": "2025-11", "revenue": 120000, "expenses": 90000},
            {"period": "2025-12", "revenue": 115000, "expenses": 88000},
        ]
        result = self.service.forecast_cash_flow(historical, 3)
        assert "forecast" in result
        assert len(result["forecast"]) == 3
        assert "summary" in result
    
    def test_break_even_calculation(self):
        """Test break-even calculation."""
        result = self.service.project_break_even(
            fixed_costs=Decimal("500000"),
            variable_cost_ratio=Decimal("0.6"),
            current_revenue=Decimal("1000000")
        )
        assert result["contribution_margin"] == 40.0
        assert result["break_even_revenue"] == 1250000
    
    def test_scenario_analysis(self):
        """Test scenario analysis."""
        result = self.service.scenario_analysis(
            Decimal("1000000"),
            Decimal("800000")
        )
        assert "optimistic" in result["scenarios"]
        assert "base" in result["scenarios"]
        assert "pessimistic" in result["scenarios"]
        assert result["scenarios"]["base"]["net_profit"] == 200000


class TestWorkingCapitalService:
    """Tests for WorkingCapitalService."""
    
    def setup_method(self):
        self.service = WorkingCapitalService()
    
    def test_analyze_working_capital(self):
        """Test working capital analysis."""
        result = self.service.analyze_working_capital(
            current_assets=Decimal("500000"),
            current_liabilities=Decimal("300000"),
            inventory=Decimal("100000"),
            receivables=Decimal("150000"),
            payables=Decimal("100000"),
            annual_revenue=Decimal("1200000"),
            cogs=Decimal("800000")
        )
        assert result["working_capital"] == 200000
        assert result["current_ratio"] > 1.5
        assert "cash_conversion_cycle" in result
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        analysis = {
            "inventory_days": 60,
            "receivable_days": 50,
            "payable_days": 20,
            "current_ratio": 1.0,
            "optimization_potential": {
                "areas": {"inventory": 15, "receivables": 20, "payables": 10}
            }
        }
        recommendations = self.service.generate_recommendations(analysis, "retail")
        assert len(recommendations) > 0


class TestFinancialProductsService:
    """Tests for FinancialProductsService."""
    
    def setup_method(self):
        self.service = FinancialProductsService()
    
    def test_recommend_products(self):
        """Test product recommendations."""
        profile = {"years_in_business": 3, "industry": "retail"}
        metrics = {
            "annual_revenue": 1000000,
            "current_ratio": 1.5,
            "cash_flow": 50000,
            "receivable_days": 30
        }
        result = self.service.recommend_products(profile, metrics)
        assert "loans" in result
        assert "insurance" in result
        assert "investments" in result
    
    def test_compare_products(self):
        """Test product comparison."""
        result = self.service.compare_products(
            ["wc_loan", "term_loan"],
            "loans"
        )
        assert "products" in result
        assert len(result["products"]) == 2
