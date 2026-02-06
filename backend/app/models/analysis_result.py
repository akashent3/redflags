"""Analysis Result model for storing analysis outcomes."""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class AnalysisResult(Base):
    """Model for storing analysis results and risk scores."""

    __tablename__ = "analysis_results"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key to Annual Report
    report_id = Column(UUID(as_uuid=True), ForeignKey('annual_reports.id', ondelete='CASCADE'), nullable=False, index=True)

    # Risk Scoring
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_level = Column(String(20), nullable=False)  # LOW, MODERATE, ELEVATED, HIGH, CRITICAL

    # Category Scores (JSON object with 8 categories)
    # {
    #     "auditor": 75,
    #     "cash_flow": 60,
    #     "related_party": 45,
    #     "promoter": 80,
    #     "governance": 30,
    #     "balance_sheet": 50,
    #     "revenue": 40,
    #     "textual": 35
    # }
    category_scores = Column(JSONB, nullable=False, default={})

    # Flag Counts
    flags_triggered_count = Column(Integer, default=0, nullable=False)
    flags_critical_count = Column(Integer, default=0, nullable=False)
    flags_high_count = Column(Integer, default=0, nullable=False)
    flags_medium_count = Column(Integer, default=0, nullable=False)
    flags_low_count = Column(Integer, default=0, nullable=False)

    # Summary
    summary_text = Column(Text, nullable=True)  # AI-generated executive summary
    key_concerns = Column(JSONB, nullable=True, default=[])  # Array of top 3-5 concerns

    # Processing Details
    analysis_version = Column(String(20), default="1.0", nullable=False)
    processing_time_seconds = Column(Integer, nullable=True)

    # Timestamps
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    # report = relationship("AnnualReport", back_populates="analyses")
    # red_flags = relationship("RedFlag", back_populates="analysis", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_analysis_report', 'report_id'),
        Index('idx_analysis_risk_score', 'risk_score'),
    )

    def __repr__(self):
        return f"<AnalysisResult(report_id='{self.report_id}', score={self.risk_score})>"

    @staticmethod
    def calculate_risk_level(score: int) -> str:
        """Calculate risk level from score (0-100)."""
        if score < 20:
            return "LOW"
        elif score < 40:
            return "MODERATE"
        elif score < 60:
            return "ELEVATED"
        elif score < 80:
            return "HIGH"
        else:
            return "CRITICAL"

    @property
    def risk_level_color(self) -> str:
        """Return color code for risk level."""
        colors = {
            "LOW": "#10b981",      # green
            "MODERATE": "#3b82f6",  # blue
            "ELEVATED": "#f59e0b",  # orange
            "HIGH": "#ef4444",      # red
            "CRITICAL": "#dc2626"   # dark red
        }
        return colors.get(self.risk_level, "#6b7280")  # gray fallback
