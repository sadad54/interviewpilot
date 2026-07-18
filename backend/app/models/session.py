from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.sql import func

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=True)
    role = Column(String, nullable=False)
    status = Column(String, default="in_progress")   # in_progress | completed
    created_at = Column(DateTime(timezone=True),  server_default=text('CURRENT_TIMESTAMP'))
  
    # Relationship with the Response model
    responses = relationship("Response", back_populates="session", cascade="all, delete-orphan")  # Assuming a Response model exists