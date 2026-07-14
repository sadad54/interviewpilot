from app.core.database import SessionLocal
from app.models.question import Question

db = SessionLocal()

questions =  [
    Question(role="Data Scientist", topic="Statistics", difficulty="easy",
             text="Explain the difference between Type I and Type II error."),
    Question(role="Data Scientist", topic="ML", difficulty="medium",
             text="Why would you choose PR-AUC over ROC-AUC for an imbalanced dataset?"),
    Question(role="AI Engineer", topic="System Design", difficulty="medium",
             text="How would you design a RAG pipeline to reduce hallucination?"),
    Question(role="AI Engineer", topic="Behavioral", difficulty="easy",
             text="Tell me about a time you had to debug a production issue under time pressure."),
]

db.add_all(questions)
db.commit()
db.close()
print(f"Seeded {len(questions)} questions into the database.")