from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.models.response import Response
from app.models.session import InterviewSession
from app.models.question import Question
from app.schemas.response import ResponseCreate, ResponseOut
from app.services.groq_client import get_groq_client
from app.services.transcription_service import transcribe_audio
from app.services.followup_service import generate_followup


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

@router.post("/audio", response_model=ResponseOut)
async def submit_audio_response(
    session_id: int = Form(...),
    question_id: int = Form(...),
    audio: UploadFile= File(...),
    db: DBSession = Depends(get_db),
):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = db.query(Question).filter(Question.id==question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    audio_bytes = await audio.read()
    if len(audio_bytes)==0:
        raise HTTPException(status_code=400, detail="Empty audio file")
    
    client = get_groq_client()
    filename = audio.filename or "audio.wav"
    try:
        transcribed_text = transcribe_audio(client, audio_bytes, filename)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Transcription failed: {str(e)}")
    
    if not transcribed_text:
        raise HTTPException(status_code=422, detail="Transcriptionr returned empty text")
    
    response = Response(session_id=session_id, question_id=question_id, answer_text=transcribed_text)
    db.add(response)
    db.commit()
    db.refresh(response)
    return response

@router.post("{/response_id}/follow-up")
def get_follow_up(response_id:int, db:DBSession = Depends(get_db) ):
    response = db.query(Response).filter(Response.id==response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    client = get_groq_client()
    try:
        result = generate_followup(
            client,
            str(response.question.text),
            str(response.answer_text),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Follow-up generation failed: {str(e)}")

    return result