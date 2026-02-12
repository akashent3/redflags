"""Annual Report model for PDF metadata."""

from sqlalchemy import Column, String, Integer, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class AnnualReport(Base):
    """Model for storing annual report PDFs metadata."""

    __tablename__ = "annual_reports"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key to Company
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False, index=True)

    # Report Details
    fiscal_year = Column(String(20), nullable=False)  # e.g., "2024-2025"  # e.g., 2023 for FY2023-24
    filing_date = Column(DateTime(timezone=True), nullable=True)

    # PDF Metadata
    pdf_url = Column(String(512), nullable=False)  # Cloudflare R2 URL
    file_size_bytes = Column(BigInteger, nullable=True)
    pages_count = Column(Integer, nullable=True)
    pdf_hash = Column(String(64), nullable=True)  # SHA-256 hash for deduplication

    # Processing Status
    is_processed = Column(String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    extraction_method = Column(String(50), nullable=True)  # pymupdf, surya_ocr, google_vision

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    # company = relationship("Company", back_populates="annual_reports")
    # analyses = relationship("AnalysisResult", back_populates="report", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_ar_company_year', 'company_id', 'fiscal_year'),
        Index('idx_ar_fiscal_year', 'fiscal_year'),
    )

    def __repr__(self):
        return f"<AnnualReport(company_id='{self.company_id}', FY={self.fiscal_year})>"

    @property
    def file_size_mb(self) -> float:
        """Return file size in MB."""
        if self.file_size_bytes:
            return round(self.file_size_bytes / (1024 * 1024), 2)
        return 0.0

    @property
    def fiscal_year_display(self) -> str:
        # Handle both string ("2024-2025") and integer (2024) formats
        if isinstance(self.fiscal_year, str):
            # Already in display format
            if "-" in self.fiscal_year:
                return f"FY {self.fiscal_year}"
            else:
                # Single year as string, convert to range
                year = int(self.fiscal_year)
                return f"FY {year}-{year + 1}"
        else:
            # Integer format
            return f"FY {self.fiscal_year}-{self.fiscal_year + 1}"
