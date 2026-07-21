from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.question import QuestionOut


class PlannedQuestion(BaseModel):
    competency: str
    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    text: str = Field(min_length=12)
    template_id: int | None = None


class InterviewPlanResult(BaseModel):
    questions: list[PlannedQuestion] = Field(min_length=5, max_length=5)


class TurnDecisionResult(BaseModel):
    should_follow_up: bool
    follow_up_question: str = ""
    decision_summary: str
    confidence: float = Field(ge=0, le=1)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class InterviewAnswerCreate(BaseModel):
    question_id: int
    answer_text: str = Field(min_length=1)
    client_request_id: str = Field(min_length=8, max_length=64)


class TranscriptTurn(BaseModel):
    question: QuestionOut
    answer_text: str | None = None
    response_id: int | None = None
    decision_summary: str | None = None


class InterviewProgress(BaseModel):
    completed_primary: int
    total_primary: int
    answered_turns: int
    elapsed_seconds: int


class InterviewStateOut(BaseModel):
    public_id: str
    status: str
    role: str
    seniority: str
    candidate_name: str | None
    plan_categories: list[str]
    current_question: QuestionOut | None
    transcript: list[TranscriptTurn]
    progress: InterviewProgress
    report_token: str | None = None


class InterviewAdvanceOut(BaseModel):
    status: str
    action: Literal["probe", "advance", "complete", "duplicate"]
    decision_summary: str
    current_question: QuestionOut | None
    progress: InterviewProgress
    report_token: str | None = None


class ReportEvidence(BaseModel):
    question_id: int
    question: str
    answer_excerpt: str
    competency: str
    score: float


class SessionReportOut(BaseModel):
    share_token: str
    session_public_id: str
    role: str
    seniority: str
    candidate_name: str | None
    overall_score: float
    competency_scores: dict[str, float]
    strengths: list[str]
    improvements: list[str]
    summary: str
    evidence: list[ReportEvidence]
    coverage_summary: dict
    transcript: list[TranscriptTurn]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
