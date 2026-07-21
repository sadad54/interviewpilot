from sqlalchemy import Boolean, Column, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)
    topic = Column(String, index=True)
    difficulty = Column(String, default="medium")
    text = Column(Text, nullable=False)
    is_template = Column(Boolean, nullable=False, default=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=True, index=True)
    template_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    parent_question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    kind = Column(String, nullable=False, default="primary")
    competency = Column(String, nullable=False, default="technical_depth")
    sequence_index = Column(Integer, nullable=True)
    planner_metadata = Column(JSON, nullable=False, default=dict)

    responses = relationship("Response", back_populates="question")
    session = relationship("InterviewSession", back_populates="questions", foreign_keys=[session_id])
    template = relationship("Question", remote_side=[id], foreign_keys=[template_id])
    parent_question = relationship("Question", remote_side=[id], foreign_keys=[parent_question_id], back_populates="follow_ups")
    follow_ups = relationship("Question", foreign_keys=[parent_question_id], back_populates="parent_question")
