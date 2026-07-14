from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.models.response import Response
from app.models.evaluation import Evaluation
from app.schemas.evaluation import EvaluationOut
from app.services.groq_client import get_groq_client
from app.services.evaluation_service import evaluate_response

router = APIRouter(prefix="/evaluations", tags=["evaluations"])

@router.post("/{response_id}", response_model=EvaluationOut)
def create_evaluation(response_id: int, db: DBSession = Depends(get_db)):
    response = db.query(Response).filter(Response.id == response_id).first()
    if not response:
        raise HTTPException(status_code=404, detail="Response not found")
    
    if response.evaluation:
        raise HTTPException(status_code=400, detail="Evaluation already exists for this response")
    
    client = get_groq_client()
    question_text = str(response.question.text) if response.question else ""
    answer_text = str(response.answer_text) if response.answer_text is not None else ""

    try:
        result = evaluate_response(
            client=client,
            question_text=question_text,
            answer_text=answer_text,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Evaluation failed: {str(e)}") from e
    
    evaluation = Evaluation(
        response_id=response.id,
        overall_score=result.overall_score,
        criteria_scores=result.criteria_scores.model_dump(),
        feedback=result.feedback,
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation