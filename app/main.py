from fastapi import FastAPI
from app.core.database import engine, Base
from app import models

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="InterviewPilpot API")

@app.get("/health")
def health_check():
    return {"status": "ok"}