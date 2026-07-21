from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.models.question import Question
from app.schemas.question import  QuestionOut

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/", response_model=list[QuestionOut])
def list_questions(role: str | None = Query(default=None), db: DBSession = Depends(get_db)):
    query = db.query(Question).filter(Question.is_template.is_(True))
    if role:
        query = query.filter(Question.role == role)
    return query.all()
@router.get("/{question_id}", response_model=QuestionOut)
def get_question(question_id: int, db: DBSession = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
