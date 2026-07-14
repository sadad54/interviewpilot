from fastapi import FastAPI
from app.core.database import engine, Base
from app import models
from app.routers import questions, responses, sessions

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="InterviewPilpot API")


app.include_router(sessions.router)
app.include_router(questions.router)
app.include_router(responses.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}