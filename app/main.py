import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from PIL import Image, UnidentifiedImageError
from app.config import settings
from app.schemas import AskRequest, AgentResponse
from app.agents.team import run_image_team, run_question_team, DISCLAIMER

app = FastAPI(title="MedAssist AI", version="1.0.0", description="Educational multi-agent medical imaging assistant")

@app.get("/", response_class=HTMLResponse)
def root():
    return "<h1>MedAssist AI API</h1><p>Educational prototype. See <a href='/docs'>/docs</a>.</p>"

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "app_name": "MedAssist AI",
        "groq_configured": bool(settings.groq_api_key),
        "model": settings.groq_model,
        "agents": ["Medical Image Analyzer", "Medical Research Agent", "Medical Report Reviewer"],
    }

@app.post("/ask", response_model=AgentResponse)
def ask(payload: AskRequest):
    try:
        answer = run_question_team(payload.question)
        return AgentResponse(status="success", question=payload.question, answer=answer, sources=[], disclaimer=DISCLAIMER)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Agent service unavailable: {exc}") from exc

@app.post("/analyze", response_model=AgentResponse)
async def analyze(file: UploadFile = File(...), question: str = Form("Describe the visible image cautiously and provide educational context.")):
    allowed = {".png", ".jpg", ".jpeg", ".bmp"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed:
        raise HTTPException(status_code=415, detail="Supported uploads: PNG, JPG, JPEG, BMP. DICOM is not supported by this demo.")
    if not question.strip() or len(question) > 2000:
        raise HTTPException(status_code=422, detail="Question must contain 1–2000 characters.")
    temp_path = None
    try:
        raw = await file.read()
        if len(raw) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Image exceeds the 10 MB upload limit.")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(raw)
            temp_path = temp.name
        try:
            with Image.open(temp_path) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise HTTPException(status_code=400, detail="Uploaded file is not a valid supported image.") from exc
        answer = run_image_team(question, temp_path)
        return AgentResponse(status="success", question=question, answer=answer, sources=[], disclaimer=DISCLAIMER)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Agent service unavailable: {exc}") from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
