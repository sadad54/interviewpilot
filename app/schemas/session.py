from datetime import datetime
from pydantic import BaseModel

class SessionCreate(BaseModel):
    role: str
    candidate_name: str | None = None  # Optional candidate name

class SessionOut(BaseModel):
    id: int
    role: str
    candidate_name: str | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True