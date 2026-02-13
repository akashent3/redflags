"""User Analysis tracking model."""

from sqlalchemy import Column, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class UserAnalysis(Base):
    """Track which users have accessed which analyses."""
    
    __tablename__ = "user_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey('analysis_results.id', ondelete='CASCADE'), nullable=False)
    accessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    analysis = relationship("AnalysisResult")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'analysis_id', name='uq_user_analysis'),
        Index('idx_user_analyses_user', 'user_id', 'accessed_at'),
        Index('idx_user_analyses_analysis', 'analysis_id'),
    )
    
    def __repr__(self):
        return f"<UserAnalysis(user_id={self.user_id}, analysis_id={self.analysis_id})>"