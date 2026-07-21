import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session as DBSession

from app.models.evaluation import Evaluation
from app.models.question import Question
from app.models.report import SessionReport
from app.models.response import Response
from app.models.session import InterviewSession
from app.schemas.evaluation import CriteriaScores, EvaluationResult
from app.schemas.interview import InterviewPlanResult, PlannedQuestion, TurnDecisionResult
from app.services.evaluation_service import evaluate_response
from app.services.followup_service import generate_followup

logger = logging.getLogger(__name__)

COMPETENCIES = [
    "technical_depth",
    "system_design",
    "problem_solving",
    "trade_offs",
    "behavioral_communication",
]

QUESTION_CATALOG: dict[str, list[tuple[str, str, str]]] = {
    "AI Engineer": [
        ("technical_depth", "Model Engineering", "How would you diagnose and reduce hallucinations in a production AI system?"),
        ("system_design", "System Design", "Design a reliable RAG service for a growing, frequently updated knowledge base."),
        ("problem_solving", "Production Debugging", "An AI endpoint suddenly becomes slower and less accurate. How would you investigate it?"),
        ("trade_offs", "Architecture", "How would you choose between fine-tuning, prompting, and retrieval for a new AI feature?"),
        ("behavioral_communication", "Behavioral", "Tell me about a technical decision you changed after receiving new evidence."),
    ],
    "Data Scientist": [
        ("technical_depth", "Statistics", "How would you validate that an observed model improvement is statistically meaningful?"),
        ("system_design", "ML Systems", "Design an experimentation and monitoring workflow for a model used in production."),
        ("problem_solving", "Data Quality", "A model's performance drops after deployment. How would you isolate the cause?"),
        ("trade_offs", "Model Selection", "How do you balance interpretability, predictive performance, and operational cost?"),
        ("behavioral_communication", "Behavioral", "Tell me about a time your analysis changed a stakeholder's decision."),
    ],
}


def _fallback_plan(session: InterviewSession, templates: list[Question]) -> InterviewPlanResult:
    catalog = QUESTION_CATALOG.get(session.role, QUESTION_CATALOG["AI Engineer"])
    template_by_competency = {q.competency: q for q in templates}
    questions = []
    for competency, topic, text in catalog:
        template = template_by_competency.get(competency)
        level_prefix = {
            "junior": "Focus on fundamentals: ",
            "senior": "At senior scope, ",
            "lead": "At staff or lead scope, ",
        }.get(session.seniority.lower(), "")
        questions.append(PlannedQuestion(
            competency=competency,
            topic=template.topic if template else topic,
            difficulty="hard" if session.seniority.lower() in {"senior", "lead"} else "medium",
            text=f"{level_prefix}{template.text if template else text}",
            template_id=template.id if template else None,
        ))
    return InterviewPlanResult(questions=questions)


def _ai_plan(client: Any, session: InterviewSession, fallback: InterviewPlanResult) -> InterviewPlanResult:
    prompt = {
        "role": session.role,
        "seniority": session.seniority,
        "job_description": (session.job_description or "")[:4000],
        "required_competencies": COMPETENCIES,
        "grounded_templates": [q.model_dump() for q in fallback.questions],
    }
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an interview planner. Return JSON with exactly five questions, one for each required competency. Adapt grounded templates without inventing company facts. Keys: questions[{competency,topic,difficulty,text,template_id}]."},
            {"role": "user", "content": json.dumps(prompt)},
        ],
        temperature=0.25,
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content
    result = InterviewPlanResult.model_validate_json(content or "{}")
    if {q.competency for q in result.questions} != set(COMPETENCIES):
        raise ValueError("Planner did not cover the required competencies")
    return result


def plan_session(db: DBSession, session: InterviewSession, client: Any | None = None) -> list[Question]:
    templates = db.query(Question).filter(Question.role == session.role, Question.is_template.is_(True)).all()
    fallback = _fallback_plan(session, templates)
    plan = fallback
    if client is not None:
        try:
            plan = _ai_plan(client, session, fallback)
        except Exception as exc:
            logger.warning("planner_fallback session=%s error=%s", session.public_id, exc)

    created = []
    for index, item in enumerate(plan.questions):
        question = Question(
            role=session.role,
            topic=item.topic,
            difficulty=item.difficulty,
            text=item.text,
            is_template=False,
            session_id=session.id,
            template_id=item.template_id,
            kind="primary",
            competency=item.competency,
            sequence_index=index,
            planner_metadata={"grounded": item.template_id is not None},
        )
        db.add(question)
        created.append(question)
    db.flush()
    session.plan_summary = {
        "categories": [q.competency for q in created],
        "question_count": len(created),
        "bounded_follow_ups": 1,
    }
    session.current_question_id = created[0].id
    session.current_primary_index = 0
    session.status = "in_progress"
    session.started_at = datetime.now(timezone.utc)
    db.commit()
    return created


def _fallback_evaluation(answer: str) -> EvaluationResult:
    words = len(answer.split())
    base = min(8, max(3, 3 + words // 25))
    return EvaluationResult(
        criteria_scores=CriteriaScores(
            technical_accuracy=base,
            clarity=min(9, base + (1 if words >= 35 else 0)),
            depth=min(9, base + (1 if words >= 70 else 0)),
        ),
        overall_score=float(base),
        feedback="The answer was recorded for the final review. Add concrete reasoning, trade-offs, and measurable outcomes to make it stronger.",
    )


def _turn_decision(client: Any | None, question: Question, answer: str, allow_probe: bool) -> TurnDecisionResult:
    if not allow_probe:
        return TurnDecisionResult(should_follow_up=False, decision_summary="Coverage recorded; advancing the interview.", confidence=1, strengths=[], gaps=[])
    if client is not None:
        try:
            raw = generate_followup(client, question.text, answer)
            return TurnDecisionResult(
                should_follow_up=bool(raw.get("should_follow_up")),
                follow_up_question=str(raw.get("follow_up_question", "")),
                decision_summary=str(raw.get("reasoning", "Answer coverage assessed.")),
                confidence=0.8,
                strengths=[],
                gaps=[],
            )
        except Exception as exc:
            logger.warning("policy_fallback question=%s error=%s", question.id, exc)
    should_probe = len(answer.split()) < 70
    return TurnDecisionResult(
        should_follow_up=should_probe,
        follow_up_question=f"Can you go deeper on the key trade-off in your approach to {question.topic.lower()}?" if should_probe else "",
        decision_summary="A targeted probe was selected because the answer needs more supporting detail." if should_probe else "The answer had enough depth to advance.",
        confidence=0.65,
        strengths=["Clear initial direction"] if answer.strip() else [],
        gaps=["Supporting detail and trade-offs"] if should_probe else [],
    )


def _next_primary(db: DBSession, session: InterviewSession, sequence_index: int) -> Question | None:
    return (
        db.query(Question)
        .filter(
            Question.session_id == session.id,
            Question.kind == "primary",
            Question.sequence_index > sequence_index,
        )
        .order_by(Question.sequence_index)
        .first()
    )


def build_report(db: DBSession, session: InterviewSession) -> SessionReport:
    if session.report:
        return session.report
    responses = db.query(Response).filter(Response.session_id == session.id).order_by(Response.id).all()
    grouped: dict[str, list[float]] = defaultdict(list)
    evidence = []
    strengths: list[str] = []
    improvements: list[str] = []
    for response in responses:
        evaluation = response.evaluation
        if not evaluation:
            continue
        competency = response.question.competency
        grouped[competency].append(float(evaluation.overall_score))
        strengths.extend(evaluation.strengths or [])
        improvements.extend(evaluation.gaps or [])
        evidence.append({
            "question_id": response.question_id,
            "question": response.question.text,
            "answer_excerpt": response.answer_text[:240],
            "competency": competency,
            "score": float(evaluation.overall_score),
        })
    competency_scores = {key: round(sum(values) / len(values), 1) for key, values in grouped.items()}
    overall = round(sum(competency_scores.values()) / len(competency_scores), 1) if competency_scores else 0.0
    unique_strengths = list(dict.fromkeys(strengths))[:4] or ["Completed a structured interview under realistic conditions"]
    unique_improvements = list(dict.fromkeys(improvements))[:4] or ["Use more specific examples and measurable outcomes"]
    report = SessionReport(
        session_id=session.id,
        overall_score=overall,
        competency_scores=competency_scores,
        strengths=unique_strengths,
        improvements=unique_improvements,
        summary=f"Completed {len(responses)} interview turns across {len(competency_scores)} competency areas.",
        evidence=evidence,
        coverage_summary={
            "planned": session.plan_summary.get("categories", []),
            "covered": list(competency_scores.keys()),
            "primary_answered": len([r for r in responses if r.question.kind == "primary"]),
            "follow_ups_answered": len([r for r in responses if r.question.kind == "follow_up"]),
        },
    )
    db.add(report)
    db.flush()
    return report


def submit_interview_answer(
    db: DBSession,
    session: InterviewSession,
    question: Question,
    answer_text: str,
    client_request_id: str,
    answer_mode: str = "text",
    client: Any | None = None,
) -> tuple[str, str, Question | None, SessionReport | None]:
    duplicate = db.query(Response).filter(Response.client_request_id == client_request_id).first()
    if duplicate:
        return "duplicate", "This answer was already processed.", session.current_question, session.report
    if session.status != "in_progress" or session.current_question_id != question.id:
        raise ValueError("Question is not the active interview turn")

    started = time.perf_counter()
    response = Response(
        session_id=session.id,
        question_id=question.id,
        answer_text=answer_text.strip(),
        client_request_id=client_request_id,
        answer_mode=answer_mode,
    )
    db.add(response)
    db.flush()

    try:
        result = evaluate_response(client, question.text, answer_text) if client is not None else _fallback_evaluation(answer_text)
    except Exception as exc:
        logger.warning("evaluation_fallback session=%s question=%s error=%s", session.public_id, question.id, exc)
        result = _fallback_evaluation(answer_text)

    allow_probe = question.kind == "primary" and not question.follow_ups
    decision = _turn_decision(client, question, answer_text, allow_probe)
    evaluation = Evaluation(
        response_id=response.id,
        overall_score=result.overall_score,
        criteria_scores=result.criteria_scores.model_dump(),
        feedback=result.feedback,
        next_action="probe" if decision.should_follow_up and allow_probe else "advance",
        strengths=decision.strengths,
        gaps=decision.gaps,
        confidence=decision.confidence,
        decision_summary=decision.decision_summary,
    )
    response.evaluation = evaluation

    base_question = question.parent_question if question.kind == "follow_up" else question
    next_question = None
    action = "advance"
    if decision.should_follow_up and allow_probe and decision.follow_up_question.strip():
        next_question = Question(
            role=session.role,
            topic=question.topic,
            difficulty=question.difficulty,
            text=decision.follow_up_question.strip(),
            is_template=False,
            session_id=session.id,
            parent_question_id=question.id,
            kind="follow_up",
            competency=question.competency,
            sequence_index=question.sequence_index,
            planner_metadata={"policy": "adaptive_probe"},
        )
        db.add(next_question)
        db.flush()
        action = "probe"
    else:
        next_question = _next_primary(db, session, int(base_question.sequence_index or 0))

    report = None
    if next_question is None:
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        session.current_question_id = None
        report = build_report(db, session)
        action = "complete"
        evaluation.next_action = "complete"
    else:
        session.current_question_id = next_question.id
        if next_question.kind == "primary":
            session.current_primary_index = int(next_question.sequence_index or 0)
    db.commit()
    logger.info("turn_processed session=%s question=%s action=%s latency_ms=%d", session.public_id, question.id, action, int((time.perf_counter() - started) * 1000))
    return action, decision.decision_summary, next_question, report
