from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    client_request_id = Column(String(64), unique=True, nullable=True, index=True)
    answer_mode = Column(String(16), nullable=False, default="text")
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))

    session = relationship("InterviewSession", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    evaluation = relationship(
        "Evaluation", back_populates="response", uselist=False, cascade="all, delete-orphan"
    )
