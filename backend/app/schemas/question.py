from pydantic import BaseModel, ConfigDict

class QuestionOut(BaseModel):
    id: int
    role: str
    topic: str
    difficulty: str
    text: str
    kind: str = "primary"
    competency: str = "technical_depth"
    sequence_index: int | None = None
    parent_question_id: int | None = None

    model_config = ConfigDict(from_attributes=True)
