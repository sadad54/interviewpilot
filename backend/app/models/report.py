import secrets

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, text
from sqlalchemy.orm import relationship

from app.core.database import Base


class SessionReport(Base):
    __tablename__ = "session_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), unique=True, nullable=False)
    share_token = Column(String(48), unique=True, index=True, nullable=False, default=lambda: secrets.token_urlsafe(24))
    overall_score = Column(Float, nullable=False)
    competency_scores = Column(JSON, nullable=False, default=dict)
    strengths = Column(JSON, nullable=False, default=list)
    improvements = Column(JSON, nullable=False, default=list)
    summary = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=False, default=list)
    coverage_summary = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    session = relationship("InterviewSession", back_populates="report")
