from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import get_db
from app.models.question import Question
from app.models.report import SessionReport
from app.models.response import Response
from app.models.session import InterviewSession
from app.schemas.interview import (
    InterviewAdvanceOut,
    InterviewAnswerCreate,
    InterviewProgress,
    InterviewStateOut,
    SessionReportOut,
    TranscriptTurn,
)
from app.schemas.question import QuestionOut
from app.schemas.session import SessionCreate, SessionOut
from app.services.groq_client import get_groq_client
from app.services.interview_service import build_report, plan_session, submit_interview_answer
from app.services.transcription_service import transcribe_audio

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _client_or_none():
    return get_groq_client() if settings.groq_api_key else None


def _get_session(public_id: str, db: DBSession) -> InterviewSession:
    session = db.query(InterviewSession).filter(InterviewSession.public_id == public_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


def _progress(session: InterviewSession) -> InterviewProgress:
    responses = session.responses
    completed_primary = len({r.question_id for r in responses if r.question.kind == "primary"})
    started = session.started_at
    end = session.completed_at or datetime.now(timezone.utc)
    if started and started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    elapsed = max(0, int((end - started).total_seconds())) if started else 0
    return InterviewProgress(
        completed_primary=completed_primary,
        total_primary=session.primary_question_count,
        answered_turns=len(responses),
        elapsed_seconds=elapsed,
    )


def _transcript(session: InterviewSession) -> list[TranscriptTurn]:
    response_by_question = {response.question_id: response for response in session.responses}
    questions = sorted(
        session.questions,
        key=lambda q: (q.sequence_index if q.sequence_index is not None else 999, 1 if q.kind == "follow_up" else 0, q.id),
    )
    turns = []
    for question in questions:
        response = response_by_question.get(question.id)
        if not response and question.id != session.current_question_id:
            continue
        turns.append(TranscriptTurn(
            question=QuestionOut.model_validate(question),
            answer_text=response.answer_text if response else None,
            response_id=response.id if response else None,
            decision_summary=response.evaluation.decision_summary if response and response.evaluation else None,
        ))
    return turns


def _state(session: InterviewSession) -> InterviewStateOut:
    return InterviewStateOut(
        public_id=session.public_id,
        status=session.status,
        role=session.role,
        seniority=session.seniority,
        candidate_name=session.candidate_name,
        plan_categories=session.plan_summary.get("categories", []),
        current_question=QuestionOut.model_validate(session.current_question) if session.current_question else None,
        transcript=_transcript(session),
        progress=_progress(session),
        report_token=session.report.share_token if session.report else None,
    )


def _report_out(report: SessionReport) -> SessionReportOut:
    session = report.session
    return SessionReportOut(
        share_token=report.share_token,
        session_public_id=session.public_id,
        role=session.role,
        seniority=session.seniority,
        candidate_name=session.candidate_name,
        overall_score=report.overall_score,
        competency_scores=report.competency_scores,
        strengths=report.strengths,
        improvements=report.improvements,
        summary=report.summary,
        evidence=report.evidence,
        coverage_summary=report.coverage_summary,
        transcript=_transcript(session),
        created_at=report.created_at,
    )


@router.post("/", response_model=SessionOut)
def create_session(payload: SessionCreate, db: DBSession = Depends(get_db)):
    session = InterviewSession(
        role=payload.role,
        candidate_name=payload.candidate_name,
        seniority=payload.seniority,
        job_description=payload.job_description,
        status="created",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{public_id}/start", response_model=InterviewStateOut)
def start_interview(public_id: str, db: DBSession = Depends(get_db)):
    session = _get_session(public_id, db)
    if session.status == "in_progress":
        return _state(session)
    if session.status != "created":
        raise HTTPException(status_code=409, detail=f"Cannot start a session with status '{session.status}'")
    session.status = "planning"
    db.commit()
    try:
        plan_session(db, session, _client_or_none())
    except Exception as exc:
        session.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"Interview planning failed: {exc}") from exc
    db.refresh(session)
    return _state(session)


@router.get("/{public_id}/state", response_model=InterviewStateOut)
def get_interview_state(public_id: str, db: DBSession = Depends(get_db)):
    return _state(_get_session(public_id, db))


@router.post("/{public_id}/answers", response_model=InterviewAdvanceOut)
def submit_interview_text_answer(public_id: str, payload: InterviewAnswerCreate, db: DBSession = Depends(get_db)):
    session = _get_session(public_id, db)
    question = db.query(Question).filter(Question.id == payload.question_id, Question.session_id == session.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question does not belong to this interview")
    try:
        action, summary, current, report = submit_interview_answer(
            db, session, question, payload.answer_text, payload.client_request_id, client=_client_or_none()
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (IntegrityError, StaleDataError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="This interview turn changed in another request. Refresh the session before retrying.") from exc
    db.refresh(session)
    return InterviewAdvanceOut(
        status=session.status,
        action=action,
        decision_summary=summary,
        current_question=QuestionOut.model_validate(current) if current else None,
        progress=_progress(session),
        report_token=report.share_token if report else None,
    )


@router.post("/{public_id}/answers/audio", response_model=InterviewAdvanceOut)
async def submit_interview_audio_answer(
    public_id: str,
    question_id: int = Form(...),
    client_request_id: str = Form(...),
    audio: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    session = _get_session(public_id, db)
    question = db.query(Question).filter(Question.id == question_id, Question.session_id == session.id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question does not belong to this interview")
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")
    client = _client_or_none()
    if client is None:
        raise HTTPException(status_code=503, detail="Audio transcription is unavailable until a Groq API key is configured")
    try:
        answer = transcribe_audio(client, audio_bytes, audio.filename or "answer.webm")
        action, summary, current, report = submit_interview_answer(
            db, session, question, answer, client_request_id, answer_mode="audio", client=client
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (IntegrityError, StaleDataError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="This interview turn changed in another request. Refresh the session before retrying.") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Audio answer failed: {exc}") from exc
    db.refresh(session)
    return InterviewAdvanceOut(
        status=session.status,
        action=action,
        decision_summary=summary,
        current_question=QuestionOut.model_validate(current) if current else None,
        progress=_progress(session),
        report_token=report.share_token if report else None,
    )


@router.post("/{public_id}/complete", response_model=SessionReportOut)
def complete_interview(public_id: str, db: DBSession = Depends(get_db)):
    session = _get_session(public_id, db)
    if session.status not in {"in_progress", "completed"}:
        raise HTTPException(status_code=409, detail="Only an active interview can be completed")
    if not session.responses:
        raise HTTPException(status_code=409, detail="Answer at least one question before finishing")
    session.status = "completed"
    session.completed_at = session.completed_at or datetime.now(timezone.utc)
    session.current_question_id = None
    report = build_report(db, session)
    db.commit()
    db.refresh(report)
    return _report_out(report)


@router.get("/{public_id}/report", response_model=SessionReportOut)
def get_session_report(public_id: str, db: DBSession = Depends(get_db)):
    session = _get_session(public_id, db)
    if not session.report:
        raise HTTPException(status_code=409, detail="The interview report is not ready")
    return _report_out(session.report)


@router.get("/reports/shared/{share_token}", response_model=SessionReportOut)
def get_shared_report(share_token: str, db: DBSession = Depends(get_db)):
    report = db.query(SessionReport).filter(SessionReport.share_token == share_token).first()
    if not report:
        raise HTTPException(status_code=404, detail="Shared report not found")
    return _report_out(report)


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: DBSession = Depends(get_db)):
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
