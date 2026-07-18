from fastapi import FastAPI
from app.core.database import engine, Base
from app import models
from app.routers import questions, responses, sessions , evaluations
from fastapi.middleware.cors import CORSMiddleware


# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="InterviewPilpot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(sessions.router)
app.include_router(questions.router)
app.include_router(responses.router)
app.include_router(evaluations.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}