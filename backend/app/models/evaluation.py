from sqlalchemy import Column, Integer, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=False)     # 0-10 scale
    criteria_scores = Column(JSON, nullable=False)    # {"clarity": 8, "technical_accuracy": 7, "structure": 6}
    feedback = Column(Text, nullable=False)

    response = relationship("Response", back_populates="evaluation")