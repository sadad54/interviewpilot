from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class SessionCreate(BaseModel):
    role: str
    candidate_name: str | None = None
    seniority: str = "mid"
    job_description: str | None = Field(default=None, max_length=8000)

class SessionOut(BaseModel):
    id: int
    public_id: str
    role: str
    candidate_name: str | None = None
    seniority: str
    job_description: str | None = None
    status: str
    primary_question_count: int
    current_primary_index: int
    plan_summary: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes= True)
