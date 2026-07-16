from pydantic import BaseModel, ConfigDict

class QuestionOut(BaseModel):
    id: int
    role: str
    topic: str
    difficulty: str
    text: str

    model_config = ConfigDict(from_attributes=True)