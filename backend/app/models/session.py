import uuid

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, text
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, index=True, nullable=False, default=lambda: str(uuid.uuid4()))
    candidate_name = Column(String, nullable=True)
    role = Column(String, nullable=False)
    seniority = Column(String, nullable=False, default="mid")
    job_description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="created")
    current_question_id = Column(Integer, ForeignKey("questions.id", use_alter=True, name="fk_session_current_question"), nullable=True)
    primary_question_count = Column(Integer, nullable=False, default=5)
    current_primary_index = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    plan_summary = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True),  server_default=text('CURRENT_TIMESTAMP'))
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
  
    # Relationship with the Response model
    responses = relationship("Response", back_populates="session", cascade="all, delete-orphan")
    questions = relationship(
        "Question",
        back_populates="session",
        cascade="all, delete-orphan",
        foreign_keys="Question.session_id",
    )
    current_question = relationship("Question", foreign_keys=[current_question_id], post_update=True)
    report = relationship("SessionReport", back_populates="session", uselist=False, cascade="all, delete-orphan")

    __mapper_args__ = {"version_id_col": version}
