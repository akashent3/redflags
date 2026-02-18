"""Red Flag model for storing individual flag results."""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class FlagSeverity(str, enum.Enum):
    """Red flag severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FlagCategory(str, enum.Enum):
    """Red flag categories."""
    AUDITOR = "Auditor"
    CASH_FLOW = "Cash Flow"
    RELATED_PARTY = "Related Party"
    PROMOTER = "Promoter"
    GOVERNANCE = "Governance"
    BALANCE_SHEET = "Balance Sheet"
    REVENUE = "Revenue"
    TEXTUAL = "Textual"


class RedFlag(Base):
    """Model for storing individual red flag results."""

    __tablename__ = "red_flags"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key to Analysis Result
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analysis_results.id', ondelete='CASCADE'), nullable=False, index=True)

    # Flag Identification
    flag_number = Column(Integer, nullable=False)  # 1-60
    flag_name = Column(String(255), nullable=False)
    flag_description = Column(Text, nullable=True)

    # Classification
    category = Column(SQLEnum(FlagCategory), nullable=False, index=True)
    severity = Column(SQLEnum(FlagSeverity), nullable=False, index=True)

    # Detection Result
    is_triggered = Column(Boolean, default=False, nullable=False, index=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100, for ML-based flags

    # Evidence
    evidence_text = Column(Text, nullable=True)  # Explanation of why flag triggered
    page_references = Column(ARRAY(Integer), nullable=True)  # Array of page numbers
    extracted_data = Column(Text, nullable=True)  # JSON string of relevant data points

    # Metadata
    detection_method = Column(String(50), nullable=True)  # rule_based, llm, hybrid
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    # analysis = relationship("AnalysisResult", back_populates="red_flags")

    # Indexes
    __table_args__ = (
        Index('idx_flag_analysis_triggered', 'analysis_id', 'is_triggered'),
        Index('idx_flag_category_severity', 'category', 'severity'),
        Index('idx_flag_number', 'flag_number'),
    )

    def __repr__(self):
        status = "TRIGGERED" if self.is_triggered else "CLEAR"
        return f"<RedFlag(#{self.flag_number}, {self.severity}, {status})>"

    @property
    def severity_points(self) -> int:
        """Return point value for severity level (for scoring)."""
        points = {
            FlagSeverity.CRITICAL: 25,
            FlagSeverity.HIGH: 15,
            FlagSeverity.MEDIUM: 8,
            FlagSeverity.LOW: 3
        }
        return points.get(self.severity, 0)

    @property
    def severity_color(self) -> str:
        """Return color code for severity level."""
        colors = {
            FlagSeverity.CRITICAL: "#dc2626",  # red-600
            FlagSeverity.HIGH: "#ea580c",      # orange-600
            FlagSeverity.MEDIUM: "#f59e0b",    # amber-500
            FlagSeverity.LOW: "#3b82f6"        # blue-500
        }
        return colors.get(self.severity, "#6b7280")  # gray-500 fallback

    @property
    def page_range_display(self) -> str:
        """Return formatted page range string."""
        if not self.page_references or len(self.page_references) == 0:
            return "N/A"
        elif len(self.page_references) == 1:
            return f"Page {self.page_references[0]}"
        else:
            pages = sorted(self.page_references)
            return f"Pages {pages[0]}-{pages[-1]}"
