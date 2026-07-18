from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, index=True)
    topic = Column(String, index=True)
    difficulty = Column(String, default="medium")
    text = Column(Text, nullable=False)
    # Relationship with the Answer model (if needed)
    # answers = relationship("Answer", back_populates="question")
    responses = relationship("Response", back_populates="question")  # Assuming a Response model exists