"""
Bookkeeping Service
Automated bookkeeping assistance with transaction categorization.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import re

from app.services.llm_service import LLMAnalyzer


class BookkeepingService:
    """Automated bookkeeping assistance."""
    
    def __init__(self):
        self.llm = LLMAnalyzer()
        
        # Common expense categories
        self.expense_categories = {
            "salary": ["salary", "wages", "payroll", "bonus", "commission"],
            "rent": ["rent", "lease", "property"],
            "utilities": ["electricity", "water", "gas", "internet", "phone", "telecom"],
            "supplies": ["office supplies", "stationery", "materials"],
            "travel": ["travel", "transport", "fuel", "petrol", "diesel", "cab", "uber", "ola"],
            "marketing": ["marketing", "advertising", "promotion", "ads", "campaign"],
            "professional_services": ["legal", "accounting", "consultant", "professional"],
            "insurance": ["insurance", "premium"],
            "equipment": ["equipment", "machinery", "hardware", "software"],
            "inventory": ["inventory", "stock", "goods", "purchase"],
            "taxes": ["tax", "gst", "tds", "income tax"],
            "bank_charges": ["bank charge", "bank fee", "transaction fee"],
            "miscellaneous": []
        }
        
        # Revenue categories
        self.revenue_categories = {
            "product_sales": ["sale", "product", "goods", "merchandise"],
            "service_revenue": ["service", "consulting", "professional fee"],
            "subscription": ["subscription", "recurring", "membership"],
            "interest_income": ["interest", "dividend"],
            "other_income": ["refund", "reimbursement", "miscellaneous"]
        }
    
    def categorize_transaction(self, description: str, amount: Decimal) -> Dict[str, Any]:
        """
        Automatically categorize a transaction based on description.
        """
        description_lower = description.lower()
        
        # Determine if income or expense
        is_income = amount > 0
        
        if is_income:
            category = self._match_category(description_lower, self.revenue_categories)
            transaction_type = "income"
        else:
            category = self._match_category(description_lower, self.expense_categories)
            transaction_type = "expense"
        
        return {
            "original_description": description,
            "category": category,
            "transaction_type": transaction_type,
            "amount": float(amount),
            "confidence": 0.85 if category != "miscellaneous" else 0.5,
            "suggested_account": self._get_account_name(category, is_income)
        }
    
    def _match_category(self, description: str, categories: Dict[str, List[str]]) -> str:
        """Match description to category based on keywords."""
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in description:
                    return category
        return "miscellaneous"
    
    def _get_account_name(self, category: str, is_income: bool) -> str:
        """Get standard account name for category."""
        account_mapping = {
            # Expense accounts
            "salary": "Salaries & Wages",
            "rent": "Rent Expense",
            "utilities": "Utilities Expense",
            "supplies": "Office Supplies",
            "travel": "Travel & Conveyance",
            "marketing": "Marketing Expense",
            "professional_services": "Professional Fees",
            "insurance": "Insurance Expense",
            "equipment": "Equipment & Depreciation",
            "inventory": "Cost of Goods Sold",
            "taxes": "Taxes & Duties",
            "bank_charges": "Bank Charges",
            "miscellaneous": "Miscellaneous Expense",
            # Revenue accounts
            "product_sales": "Sales Revenue",
            "service_revenue": "Service Income",
            "subscription": "Subscription Revenue",
            "interest_income": "Interest Income",
            "other_income": "Other Income"
        }
        return account_mapping.get(category, "Miscellaneous")
    
    def detect_duplicates(self, transactions: List[Dict]) -> List[Dict]:
        """
        Detect potential duplicate transactions.
        """
        duplicates = []
        seen = {}
        
        for i, txn in enumerate(transactions):
            # Create a key based on amount and date
            key = f"{txn.get('amount')}_{txn.get('date')}"
            
            if key in seen:
                duplicates.append({
                    "transaction_1": seen[key],
                    "transaction_2": txn,
                    "reason": "Same amount and date",
                    "confidence": 0.8
                })
            else:
                seen[key] = txn
        
        return duplicates
    
    def reconcile_accounts(
        self,
        book_balance: Decimal,
        bank_balance: Decimal,
        uncleared_transactions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Perform bank reconciliation.
        """
        # Calculate uncleared amounts
        uncleared_deposits = sum(
            Decimal(str(t['amount'])) 
            for t in uncleared_transactions 
            if t.get('type') == 'deposit'
        )
        uncleared_payments = sum(
            Decimal(str(t['amount'])) 
            for t in uncleared_transactions 
            if t.get('type') == 'payment'
        )
        
        # Calculate adjusted book balance
        adjusted_book = book_balance + uncleared_deposits - uncleared_payments
        
        # Calculate difference
        difference = bank_balance - adjusted_book
        
        is_reconciled = abs(difference) < Decimal('0.01')
        
        return {
            "book_balance": float(book_balance),
            "bank_balance": float(bank_balance),
            "uncleared_deposits": float(uncleared_deposits),
            "uncleared_payments": float(uncleared_payments),
            "adjusted_book_balance": float(adjusted_book),
            "difference": float(difference),
            "is_reconciled": is_reconciled,
            "status": "Reconciled" if is_reconciled else "Discrepancy Found",
            "suggestions": [] if is_reconciled else [
                "Review uncleared transactions",
                "Check for missing bank entries",
                "Verify all deposits are recorded"
            ]
        }
    
    def generate_journal_entry(
        self,
        transaction_type: str,
        amount: Decimal,
        description: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Generate a double-entry journal entry.
        """
        entries = []
        
        if transaction_type == "expense":
            # Debit expense account, Credit cash/bank
            entries = [
                {
                    "account": self._get_account_name(category, False),
                    "debit": float(amount),
                    "credit": 0
                },
                {
                    "account": "Cash/Bank",
                    "debit": 0,
                    "credit": float(amount)
                }
            ]
        elif transaction_type == "income":
            # Debit cash/bank, Credit revenue account
            entries = [
                {
                    "account": "Cash/Bank",
                    "debit": float(amount),
                    "credit": 0
                },
                {
                    "account": self._get_account_name(category, True),
                    "debit": 0,
                    "credit": float(amount)
                }
            ]
        
        return {
            "date": datetime.utcnow().isoformat(),
            "description": description,
            "entries": entries,
            "total_debit": float(amount),
            "total_credit": float(amount),
            "is_balanced": True
        }
    
    def batch_categorize(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize multiple transactions at once.
        """
        categorized = []
        for txn in transactions:
            result = self.categorize_transaction(
                txn.get('description', ''),
                Decimal(str(txn.get('amount', 0)))
            )
            result['original_transaction'] = txn
            categorized.append(result)
        
        return categorized
