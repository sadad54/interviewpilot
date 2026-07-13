from fastapi import FastAPI

app = FastAPI(title="InterviewPilpot API")

@app.get("/health")
def health_check():
    return {"status": "ok"}