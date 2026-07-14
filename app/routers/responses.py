from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.models.response import Response
from app.models.session import InterviewSession
from app.models.question import Question
from app.schemas.response import ResponseCreate, ResponseOut

router = APIRouter(prefix="/responses", tags=["responses"])

@router.post("/", response_model=ResponseOut)
def submit_response(payload: ResponseCreate, db: DBSession = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    question = db.query(Question).filter(Question.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    response = Response(
        session_id=payload.session_id,
        question_id=payload.question_id,
        answer_text=payload.answer_text
    )
    db.add(response)
    db.commit()
    db.refresh(response)
    return response