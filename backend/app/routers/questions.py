from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.models.question import Question
from app.schemas.question import  QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/", response_model=list[QuestionOut])
def list_questions(role: str | None = Query(default=None), db: DBSession = Depends(get_db)):
    query = db.query(Question)
    if role:
        query = query.filter(Question.role == role)
    return query.all()