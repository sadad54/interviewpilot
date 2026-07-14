from datetime import datetime
from pydantic import BaseModel

class ResponseCreate(BaseModel):
    session_id: int
    question_id: int
    answer_text: str

class ResponseOut(BaseModel):
    id: int
    session_id: int
    question_id: int
    answer_text: str
    created_at: datetime

    class Config:
        from_attributes = True