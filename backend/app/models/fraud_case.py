"""Fraud case models for pattern matching and historical fraud analysis."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID

from app.database import Base


class FraudCase(Base):
    """Historical fraud case for pattern matching."""

    __tablename__ = "fraud_cases"

    # Primary Key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Case Identification
    case_id = Column(String(100), unique=True, nullable=False, index=True)  # e.g., 'satyam-2009'
    company_name = Column(String(300), nullable=False)
    year = Column(Integer, nullable=False)

    # Classification
    sector = Column(String(100), nullable=True)
    industry = Column(String(255), nullable=True)
    fraud_type = Column(String(100), nullable=False)  # e.g., 'Accounting Fraud', 'Promoter Diversion'
    detection_difficulty = Column(String(50), nullable=True)  # 'Easy', 'Medium', 'Hard'

    # Financial Impact
    stock_decline_percent = Column(Numeric(10, 2), nullable=True)  # e.g., -97.40
    market_cap_lost_cr = Column(Numeric(15, 2), nullable=True)  # in crores

    # Analysis Data (JSONB for flexibility)
    primary_flags = Column(JSONB, nullable=True)  # ['Flag 1', 'Flag 2']
    timeline = Column(JSONB, nullable=True)  # [{date, event, type}]
    red_flags_detected = Column(JSONB, nullable=False)  # [{flag_number, flag_name, evidence, when_visible}]
    what_investors_missed = Column(JSONB, nullable=True)  # ['Point 1', 'Point 2']
    lessons_learned = Column(JSONB, nullable=True)  # ['Lesson 1', 'Lesson 2']

    # Outcome & Regulatory Action
    outcome = Column(Text, nullable=True)
    regulatory_action = Column(Text, nullable=True)

    # PDF Document URL (stored in R2)
    pdf_url = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by_user_id = Column(PostgresUUID(as_uuid=True), nullable=True)  # Admin who uploaded

    def __repr__(self):
        return f"<FraudCase(case_id='{self.case_id}', company='{self.company_name}', year={self.year})>"

    @property
    def triggered_flag_numbers(self):
        """Extract list of flag numbers from red_flags_detected."""
        if not self.red_flags_detected:
            return []
        return [flag.get("flag_number") for flag in self.red_flags_detected if flag.get("flag_number")]
