"""
FastAPI entry for r3d_drag0n7 Dragon Studio.
Serve with: uvicorn web.app:app --reload --port 7860
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from web.chart_service import live_ai_reading, run_chart, sistema_status

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="r3d_drag0n7 Dragon Studio",
    description="Celestial Chinese-dragon natal chart API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost:7860",
        "http://127.0.0.1:7860",
        "http://localhost:5500",
        "https://wifiknight45.github.io",
        "https://wifiknight45.github.io/r3d_drag0n7",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChartRequest(BaseModel):
    name: Optional[str] = None
    date: str = Field(..., description="YYYY-MM-DD or slash date")
    time: Optional[str] = "12:00"
    place: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    timezone: Optional[str] = None
    house_system: Optional[str] = "Placidus"
    mode: Optional[str] = "Ptolemy"


class AIReadingRequest(BaseModel):
    chart: Dict[str, Any]
    question: Optional[str] = None


@app.get("/api/health")
def health():
    return {"ok": True, "sistema": sistema_status()}


@app.post("/api/chart")
def api_chart(body: ChartRequest):
    result = run_chart(body.model_dump())
    status = 200 if result.get("ok") else 400
    return JSONResponse(content=result, status_code=status)


@app.post("/api/ai/reading")
async def api_ai_reading(body: AIReadingRequest):
    result = await live_ai_reading(body.chart, body.question)
    status = 200 if result.get("ok") else 400
    return JSONResponse(content=result, status_code=status)


@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return JSONResponse({"error": "frontend missing"}, status_code=404)
    return FileResponse(index_path)


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.exception_handler(Exception)
async def unhandled(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": str(exc), "path": str(request.url.path)},
    )
