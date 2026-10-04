from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.models import GenerateRequest, GenerateResponse
from app.services.media_generator import generate_media

app = FastAPI(title="AI Media Chatbot", version="1.0.0")

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def home():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "AI Media Chatbot is running"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate_api(request: GenerateRequest):
    try:
        result = generate_media(prompt=request.prompt, media_type=request.media_type)
        return GenerateResponse(
            media_type=result["media_type"],
            prompt=result["prompt"],
            file_path=result["file_path"],
            message=result["message"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/health")
def health():
    return {"status": "ok"}
