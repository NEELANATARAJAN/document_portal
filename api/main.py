from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from typing import Dict, List, Any, Optional
import os
from pathlib import Path

app = FastAPI(title="Document Portal API", version="0.1")

# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = current_dir = os.getcwd()
app.mount("/static", StaticFiles(directory=str(os.path.join(BASE_DIR, "static"))), name="static")
templates = Jinja2Templates(directory=str(os.path.join(BASE_DIR, "templates")))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
# /Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/api/main.py
# /Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/static

# current_dir = os.getcwd()
# static_dir = os.path.join(current_dir , "static")
# templates_dir = os.path.join(current_dir, "templates")

# # serve static and templates
# app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
# templates=Jinja2Templates(director=str(templates_dir))

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "document-portal"}

@app.post("/analyze")
async def analyze_document(file:UploadFile = File(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status=500, detail=f"Analysis Failed: {e}")

@app.post("/compare")
async def compare_document(reference: UploadFile=File(...), actual: UploadFile=File(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status=500, detail=f"Compare documents Failed: {e}")

@app.post("/chat/index")
async def chat_build_index() -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status=500, detail=f"Indexing Failed {e}")

@app.post("/chat/query")
async def chat_query():
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status=500, detail=f"Chat Query failed : {e}")

