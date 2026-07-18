from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SessionCreate(BaseModel):
    role: str
    candidate_name: str | None = None  # Optional candidate name

class SessionOut(BaseModel):
    id: int
    role: str
    candidate_name: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes= True)