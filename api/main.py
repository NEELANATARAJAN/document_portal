from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from jose import jwt # type: ignore
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
import os
from pathlib import Path
from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_ingestion.data_ingestion import (
    DocumentHandler, 
    DocumentComparator, 
    ChatIngestor,
    FaissManager)
from src.document_compare.document_comparator import DocumentComparatorLLM
from src.document_chat.retrieval import ConversationalRAG
from utils.document_ops import read_pdf_via_handler
from passlib.context import CryptContext
from logger import GLOBAL_LOGGER as log
from dotenv import load_dotenv

# load_dotenv()

# Set the global cache
set_llm_cache(InMemoryCache())

FAISS_BASE = os.getenv("FAISS_BASE", "faiss_index")
UPLOAD_BASE = os.getenv("UPLOAD_BASE", "data")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "index")

app = FastAPI(title="Document Portal API", version="0.1")

BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = current_dir = os.getcwd()
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


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

users_db = {
    "admin@example.com": {
        "username": "admin@example.com",
        "hashed_password": "$2b$12$11DT78Pv1oTyoSHDVvRR0esLSatxjE7MG.L2JTrZJLhB4apZZYqxS"  # hashed "
    }
}

SECRET_KEY = "9yWmOZ9xQcnXxy4nHRmDdMIePtRxlZAgEfVu1R8Oxnb9pJXeInqBJpID8Hd1tYyB"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("password123")
print("Use this hash in your users_db:\n", hashed)

ALGORITHM = "HS256"

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request: Request):
    log.info("Serving UI homepage")
    return templates.TemplateResponse("login.html", {"request": request})
    # # resp = templates.TemplateResponse("index.html", {"request": request})
    # resp = templates.TemplateResponse(request, "index.html", {"request": request})
    # resp.headers["Cache-Control"] = "no-store"
    # return resp

@app.get("/health")
def health() -> Dict[str, str]:
    log.info("Health Check passed.")
    return {"status": "ok", "service": "document-portal"}

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = users_db.get(username)
    print("Username entered: ", username)
    print("\n\nUser got: ", user)
    print("User name:", user["username"] if user else "No user found")
    print("Password entered: ", password)
    print("Hashed password: ", user["hashed_password"] if user else "No user found")
    print("Password verified: ", pwd_context.verify(password, user["hashed_password"]) if user else "No user found")
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        log.warning(f"Failed login attempt for user: {username}")
        return templates.TemplateResponse("login.html", {'request': request, "error": "Invalid credentials"}, status_code=401)    
    # In a real application, generate and return a JWT token here
    log.info(f"User {username} logged in successfully.")
    access_token = jwt.encode(
        {"sub": username, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    response = templates.TemplateResponse("index.html", {"request": request, "username": username}, status_code=200)
    response.set_cookie("access_token", access_token)
    response.headers["Cache-Control"] = "no-store"
    return response

class FastAPIFileAdapter:
    """Adapt FastAPI UploadFile -> .name + .getbuffer() API"""
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename
    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()

@app.post("/analyze")
async def analyze_document(file:UploadFile = File(...)) -> Any:
    try:
        log.info(f"Received file for analysis: {file.filename}")
        dh = DocumentHandler()
        save_path=dh.save_pdf(FastAPIFileAdapter(file))
        text = read_pdf_via_handler(dh, save_path)

        analyzer = DocumentAnalyzer()

        result = analyzer.analyze_document(text)
        log.info("Document Analysis complete.")
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Error during document analysis")
        raise HTTPException(status=500, detail=f"Analysis Failed: {e}")

@app.post("/compare")
async def compare_document(reference: UploadFile=File(...), actual: UploadFile=File(...)) -> Any:
    try:
        log.info(f"Comparing files: {reference.filename} vs {actual.filename}")
        dc = DocumentComparator()
        ref_path, actual_path = dc.save_upload_files(FastAPIFileAdapter(reference), FastAPIFileAdapter(actual))
        _ = ref_path, actual_path
        combined_text = dc.combine_documents()
        comp = DocumentComparatorLLM()
        df = comp.compare_documents(combined_docs=combined_text)
        log.info("Document Comparison completed.")
        return {"rows": df.to_dict(orient="records"), "session_id": dc.session_id}
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Comparison failed")
        raise HTTPException(status=500, detail=f"Compare documents Failed: {e}")

@app.post("/chat/index")
async def chat_build_index(
    files: List[UploadFile] = File(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    chunk_size: int = Form(1000),
    chunk_overlap: int = Form(200),
    k: int = Form(5),
) -> Any:
    try:
        log.info(f"Indexing chat session. Session ID: {session_id}, Files: {[f.filename for f in files]}")
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
        ci.build_retriever(wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        log.info(f"Index created successfully for session: {ci.session_id}")
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    
    except HTTPException:
        raise
    except Exception as e:
        log.exception("Chat index building failed")
        raise HTTPException(status=500, detail=f"Indexing Failed {e}")

@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
):
    try:
        log.info(f"Received chat query: '{question}' | session: {session_id}")
        start = datetime.utcnow()
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs is True")
        
        # Prepare FAISS Index
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE # type: ignore
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"FAISS Index not found in {index_dir}")
        
        # Initialize LCEL-style RAG Pipeline
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir, k=k, index_name=FAISS_INDEX_NAME)

        # Optional: for now we will pass empty chat history
        response = rag.invoke(question, chat_history=[])
        log.info("Chat query handled successfully")
        end = datetime.utcnow()
        duration = (end - start).total_seconds() * 1000
        log.info(f"\n\n==============Cache comparison =================\n")
        log.info(f"✅  Response Duration: {duration:.2f} ms\n\n")
        print(f"\n\n==============Cache comparison =================\n")
        print(f"✅  Response Duration: {duration:.2f} ms\n\n")

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG",
        }

    except HTTPException:
        raise
    except Exception as e:
        log.info("Chat query failed.")
        raise HTTPException(status=500, detail=f"Chat Query failed : {e}")

