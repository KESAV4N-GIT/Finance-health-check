"""
Tax Compliance Service
GST compliance checking and tax calculations for India.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class GSTSlabRate(Enum):
    """GST slab rates in India."""
    ZERO = 0
    FIVE = 5
    TWELVE = 12
    EIGHTEEN = 18
    TWENTY_EIGHT = 28


class TaxComplianceService:
    """Tax compliance checking for Indian SMEs."""
    
    # GST filing due dates (simplified)
    GST_DUE_DATES = {
        "GSTR-1": 11,  # 11th of following month
        "GSTR-3B": 20,  # 20th of following month
        "GSTR-9": 31,  # 31st December of next FY
    }
    
    # TDS rates
    TDS_RATES = {
        "salary": 0,  # Depends on tax slab
        "professional_fees": 10,
        "rent": 10,
        "contractor": 1,  # Individual
        "contractor_company": 2,
        "interest": 10,
    }
    
    def validate_gstin(self, gstin: str) -> Dict[str, Any]:
        """
        Validate GSTIN format and structure.
        
        GSTIN format: 22AAAAA0000A1Z5
        - First 2 digits: State code
        - Next 10 characters: PAN
        - 13th character: Entity number
        - 14th character: Z (default)
        - 15th character: Check digit
        """
        gstin = gstin.upper().strip()
        errors = []
        
        # Length check
        if len(gstin) != 15:
            errors.append("GSTIN must be exactly 15 characters")
        
        # Format check
        import re
        pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        if not re.match(pattern, gstin):
            errors.append("Invalid GSTIN format")
        
        # State code validation (01-37)
        if len(gstin) >= 2:
            try:
                state_code = int(gstin[:2])
                if state_code < 1 or state_code > 37:
                    errors.append("Invalid state code")
            except ValueError:
                errors.append("State code must be numeric")
        
        return {
            "gstin": gstin,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "state_code": gstin[:2] if len(gstin) >= 2 else None,
            "pan": gstin[2:12] if len(gstin) >= 12 else None,
        }
    
    def calculate_gst(
        self,
        amount: Decimal,
        gst_rate: GSTSlabRate,
        is_interstate: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate GST components.
        
        For intrastate: CGST + SGST (each at half the rate)
        For interstate: IGST (full rate)
        """
        rate = Decimal(str(gst_rate.value)) / 100
        gst_amount = amount * rate
        
        if is_interstate:
            return {
                "base_amount": float(amount),
                "gst_rate": gst_rate.value,
                "igst": float(gst_amount),
                "cgst": 0,
                "sgst": 0,
                "total_gst": float(gst_amount),
                "total_amount": float(amount + gst_amount),
                "type": "Interstate"
            }
        else:
            half_gst = gst_amount / 2
            return {
                "base_amount": float(amount),
                "gst_rate": gst_rate.value,
                "igst": 0,
                "cgst": float(half_gst),
                "sgst": float(half_gst),
                "total_gst": float(gst_amount),
                "total_amount": float(amount + gst_amount),
                "type": "Intrastate"
            }
    
    def check_gst_compliance(
        self,
        gst_data: Dict,
        current_date: date = None
    ) -> Dict[str, Any]:
        """
        Check GST compliance status and generate alerts.
        """
        current_date = current_date or date.today()
        issues = []
        warnings = []
        
        # Check GSTR-1 filing
        gstr1_due = self._get_due_date("GSTR-1", gst_data.get("period"))
        if gst_data.get("gstr1_filed") is False and current_date > gstr1_due:
            issues.append({
                "type": "GSTR-1 Not Filed",
                "severity": "high",
                "due_date": gstr1_due.isoformat(),
                "action": "File GSTR-1 immediately to avoid late fees"
            })
        
        # Check GSTR-3B filing
        gstr3b_due = self._get_due_date("GSTR-3B", gst_data.get("period"))
        if gst_data.get("gstr3b_filed") is False and current_date > gstr3b_due:
            issues.append({
                "type": "GSTR-3B Not Filed",
                "severity": "critical",
                "due_date": gstr3b_due.isoformat(),
                "action": "File GSTR-3B immediately. Interest will be charged on late payment."
            })
        
        # Check ITC reconciliation
        output_tax = Decimal(str(gst_data.get("output_tax", 0)))
        input_tax = Decimal(str(gst_data.get("input_tax", 0)))
        
        if input_tax > output_tax * Decimal("1.5"):
            warnings.append({
                "type": "High ITC Claim",
                "severity": "medium",
                "message": "Input tax credit is significantly higher than output tax. May trigger scrutiny.",
                "action": "Verify all ITC claims have valid invoices"
            })
        
        # Calculate late fee if applicable
        late_fee = self._calculate_late_fee(
            gst_data.get("liability", 0),
            gst_data.get("filing_date"),
            gstr3b_due
        )
        
        compliance_score = 100
        compliance_score -= len(issues) * 25
        compliance_score -= len(warnings) * 10
        compliance_score = max(0, compliance_score)
        
        return {
            "compliance_score": compliance_score,
            "status": "Compliant" if compliance_score >= 80 else "Non-Compliant",
            "issues": issues,
            "warnings": warnings,
            "late_fee_estimate": late_fee,
            "next_due_dates": {
                "GSTR-1": gstr1_due.isoformat(),
                "GSTR-3B": gstr3b_due.isoformat()
            }
        }
    
    def _get_due_date(self, return_type: str, period: str) -> date:
        """Get due date for a GST return."""
        # Simplified: assumes period is in format "MM-YYYY"
        try:
            month, year = period.split("-")
            due_day = self.GST_DUE_DATES.get(return_type, 20)
            
            # Due date is in the following month
            due_month = int(month) + 1
            due_year = int(year)
            if due_month > 12:
                due_month = 1
                due_year += 1
            
            return date(due_year, due_month, due_day)
        except:
            return date.today()
    
    def _calculate_late_fee(
        self,
        liability: float,
        filing_date: str,
        due_date: date
    ) -> Dict[str, Any]:
        """Calculate late filing fee and interest."""
        if not filing_date:
            # Not yet filed
            days_late = (date.today() - due_date).days
        else:
            try:
                filed = datetime.fromisoformat(filing_date).date()
                days_late = (filed - due_date).days
            except:
                days_late = 0
        
        if days_late <= 0:
            return {"late_fee": 0, "interest": 0, "total": 0}
        
        # CGST late fee: Rs. 50/day (max Rs. 5000)
        # SGST late fee: Rs. 50/day (max Rs. 5000)
        late_fee = min(days_late * 100, 10000)  # Combined CGST + SGST
        
        # Interest: 18% p.a. on tax liability
        interest = liability * 0.18 * (days_late / 365)
        
        return {
            "days_late": days_late,
            "late_fee": late_fee,
            "interest": round(interest, 2),
            "total": round(late_fee + interest, 2)
        }
    
    def calculate_tds(
        self,
        amount: Decimal,
        payment_type: str,
        is_pan_available: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate TDS deduction.
        """
        rate = self.TDS_RATES.get(payment_type, 10)
        
        # Higher rate if PAN not available
        if not is_pan_available:
            rate = 20
        
        tds_amount = amount * Decimal(str(rate)) / 100
        
        return {
            "gross_amount": float(amount),
            "payment_type": payment_type,
            "tds_rate": rate,
            "tds_amount": float(tds_amount),
            "net_payable": float(amount - tds_amount),
            "pan_available": is_pan_available
        }
    
    def generate_compliance_checklist(self, period: str) -> List[Dict]:
        """
        Generate tax compliance checklist for a period.
        """
        return [
            {
                "item": "GSTR-1 Filing",
                "description": "Sales return with invoice-wise details",
                "due_date": self._get_due_date("GSTR-1", period).isoformat(),
                "priority": "high"
            },
            {
                "item": "GSTR-3B Filing",
                "description": "Summary return with tax payment",
                "due_date": self._get_due_date("GSTR-3B", period).isoformat(),
                "priority": "critical"
            },
            {
                "item": "TDS Payment",
                "description": "Deposit TDS deducted during the month",
                "due_date": f"7th of following month",
                "priority": "high"
            },
            {
                "item": "Advance Tax",
                "description": "Quarterly advance tax if liability > Rs. 10,000",
                "due_date": "15th of quarter end month",
                "priority": "medium"
            },
            {
                "item": "ITC Reconciliation",
                "description": "Match ITC claims with GSTR-2A/2B",
                "due_date": "Before GSTR-3B filing",
                "priority": "high"
            }
        ]
    
    def identify_tax_deductions(self, expenses: List[Dict]) -> Dict[str, Any]:
        """
        Identify potential tax deductions from expenses.
        """
        deductible = []
        total_deductions = Decimal("0")
        
        deduction_categories = {
            "rent": "Section 30 - Rent for business premises",
            "salary": "Section 36 - Salaries and wages",
            "insurance": "Section 36 - Insurance premiums",
            "depreciation": "Section 32 - Depreciation on assets",
            "professional_fees": "Section 37 - Professional fees",
            "travel": "Section 37 - Travel for business",
            "marketing": "Section 37 - Advertisement and marketing"
        }
        
        for expense in expenses:
            category = expense.get("category", "").lower()
            amount = Decimal(str(expense.get("amount", 0)))
            
            for key, section in deduction_categories.items():
                if key in category:
                    deductible.append({
                        "expense": expense.get("description"),
                        "amount": float(amount),
                        "category": category,
                        "tax_section": section,
                        "deductible": True
                    })
                    total_deductions += amount
                    break
        
        return {
            "deductible_expenses": deductible,
            "total_deductions": float(total_deductions),
            "potential_tax_savings": float(total_deductions * Decimal("0.30")),  # Assuming 30% slab
            "recommendations": [
                "Maintain proper documentation for all deductions",
                "Ensure GST input tax credit is claimed where applicable",
                "Consider depreciation on all business assets"
            ]
        }
