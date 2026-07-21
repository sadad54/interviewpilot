from app.core.database import SessionLocal
from app.models.question import Question
from app.services.interview_service import QUESTION_CATALOG


def seed_question_bank():
    db = SessionLocal()
    created = 0
    try:
        for role, questions in QUESTION_CATALOG.items():
            for competency, topic, text in questions:
                exists = db.query(Question).filter(
                    Question.role == role,
                    Question.text == text,
                    Question.is_template.is_(True),
                ).first()
                if exists:
                    exists.competency = competency
                    exists.topic = topic
                    continue
                db.add(Question(
                    role=role,
                    topic=topic,
                    difficulty="medium",
                    text=text,
                    is_template=True,
                    kind="primary",
                    competency=competency,
                ))
                created += 1
        db.commit()
    finally:
        db.close()
    print(f"Question bank ready. Added {created} templates.")


if __name__ == "__main__":
    seed_question_bank()
