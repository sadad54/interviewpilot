from pydantic import BaseModel

class QuestionOut(BaseModel):
    id: int
    role: str
    topic: str
    difficulty: str
    text: str

    class Config:
        from_attributes = True