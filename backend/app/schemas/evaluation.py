from pydantic import BaseModel, ConfigDict, Field

class CriteriaScores(BaseModel):
    technical_accuracy:int = Field(ge=0, le=10)
    clarity:int = Field(ge=0, le=10)
    depth:int = Field(ge=0, le=10)

class EvaluationResult(BaseModel):
    """This is the exact shape we force the LLM to return."""
    criteria_scores: CriteriaScores
    overall_score: float = Field(ge=0, le=10)
    feedback: str

class EvaluationOut(BaseModel):
    id: int
    response_id: int
    overall_score: float
    criteria_scores: dict
    feedback: str
    next_action: str | None = None
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    confidence: float | None = None
    decision_summary: str | None = None

    model_config = ConfigDict(from_attributes=True)
