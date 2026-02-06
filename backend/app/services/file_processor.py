"""
File Processor Service
Handles file validation, encryption, and parsing.
"""
import os
import uuid
from datetime import datetime
from typing import Optional
from cryptography.fernet import Fernet
import pandas as pd
import PyPDF2
import pdfplumber

from app.core.config import settings
from app.models.financial_data import FileType, ProcessingStatus
from app.schemas.upload import FileValidationResponse


class FileProcessor:
    """Handles file upload processing and encryption."""
    
    def __init__(self):
        # Initialize encryption key (in production, use proper key management)
        self.fernet = Fernet(Fernet.generate_key())
    
    async def save_encrypted_file(
        self,
        content: bytes,
        filename: str,
        user_id: int
    ) -> str:
        """
        Encrypt and save uploaded file.
        
        Returns path to encrypted file.
        """
        # Generate unique filename
        ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
        unique_name = f"{user_id}_{uuid.uuid4().hex}.{ext}.enc"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        
        # Encrypt content
        encrypted_content = self.fernet.encrypt(content)
        
        # Save encrypted file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(encrypted_content)
        
        return file_path
    
    async def read_encrypted_file(self, file_path: str) -> bytes:
        """Read and decrypt a file."""
        with open(file_path, "rb") as f:
            encrypted_content = f.read()
        return self.fernet.decrypt(encrypted_content)
    
    async def validate_file(
        self,
        content: bytes,
        file_type: FileType
    ) -> FileValidationResponse:
        """
        Validate file content and structure.
        """
        errors = []
        warnings = []
        column_count = None
        row_count = None
        detected_format = None
        
        try:
            if file_type == FileType.CSV:
                df = pd.read_csv(pd.io.common.BytesIO(content))
                column_count = len(df.columns)
                row_count = len(df)
                detected_format = self._detect_csv_format(df)
                
                # Validate required columns
                if row_count == 0:
                    errors.append("CSV file is empty")
                elif column_count < 2:
                    warnings.append("CSV has fewer than 2 columns")
                    
            elif file_type == FileType.XLSX:
                df = pd.read_excel(pd.io.common.BytesIO(content))
                column_count = len(df.columns)
                row_count = len(df)
                detected_format = "excel_general"
                
                if row_count == 0:
                    errors.append("Excel file has no data rows")
                    
            elif file_type == FileType.PDF:
                # Validate PDF
                reader = PyPDF2.PdfReader(pd.io.common.BytesIO(content))
                page_count = len(reader.pages)
                
                if page_count == 0:
                    errors.append("PDF has no pages")
                else:
                    detected_format = "pdf_document"
                    row_count = page_count
                    
        except pd.errors.EmptyDataError:
            errors.append("File is empty or has invalid format")
        except Exception as e:
            errors.append(f"Error processing file: {str(e)}")
        
        return FileValidationResponse(
            is_valid=len(errors) == 0,
            file_type=file_type,
            detected_format=detected_format,
            column_count=column_count,
            row_count=row_count,
            errors=errors,
            warnings=warnings
        )
    
    def _detect_csv_format(self, df: pd.DataFrame) -> str:
        """Detect the type of financial data in CSV."""
        columns_lower = [c.lower() for c in df.columns]
        
        # Bank statement detection
        if any(col in columns_lower for col in ["transaction", "debit", "credit", "balance"]):
            return "bank_statement"
        
        # P&L detection
        if any(col in columns_lower for col in ["revenue", "income", "expense", "profit"]):
            return "profit_loss"
        
        # GST return detection
        if any(col in columns_lower for col in ["gst", "gstin", "tax", "igst", "cgst"]):
            return "gst_return"
        
        return "general_financial"
    
    async def process_file_async(
        self,
        file_id: int,
        encrypted_path: str,
        file_type: FileType
    ):
        """
        Background task to process uploaded file.
        
        This would update the database with extracted data.
        """
        # In production, this would:
        # 1. Decrypt the file
        # 2. Parse based on file type
        # 3. Extract financial data
        # 4. Store in appropriate tables
        # 5. Update processing status
        pass
    
    async def parse_csv(self, content: bytes) -> dict:
        """Parse CSV file and extract financial data."""
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        return {
            "columns": list(df.columns),
            "row_count": len(df),
            "data": df.to_dict(orient="records")[:100]  # First 100 rows
        }
    
    async def parse_excel(self, content: bytes) -> dict:
        """Parse Excel file and extract financial data."""
        # Read all sheets
        xlsx = pd.ExcelFile(pd.io.common.BytesIO(content))
        sheets_data = {}
        
        for sheet_name in xlsx.sheet_names:
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            sheets_data[sheet_name] = {
                "columns": list(df.columns),
                "row_count": len(df),
                "data": df.to_dict(orient="records")[:100]
            }
        
        return {"sheets": sheets_data}
    
    async def parse_pdf(self, content: bytes) -> dict:
        """Parse PDF file and extract text/tables."""
        extracted_data = {
            "text": [],
            "tables": []
        }
        
        with pdfplumber.open(pd.io.common.BytesIO(content)) as pdf:
            for page in pdf.pages:
                # Extract text
                text = page.extract_text()
                if text:
                    extracted_data["text"].append(text)
                
                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    if len(table) > 1:
                        headers = table[0]
                        rows = table[1:]
                        extracted_data["tables"].append({
                            "headers": headers,
                            "rows": rows[:50]  # First 50 rows
                        })
        
        return extracted_data
