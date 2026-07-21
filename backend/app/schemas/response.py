from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ResponseCreate(BaseModel):
    session_id: int
    question_id: int
    answer_text: str
    client_request_id: str | None = None


class ResponseOut(BaseModel):
    id: int
    session_id: int
    question_id: int
    answer_text: str
    client_request_id: str | None = None
    answer_mode: str = "text"
    created_at: datetime

    model_config =ConfigDict(from_attributes=True)
