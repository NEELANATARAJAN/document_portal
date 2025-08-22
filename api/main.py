from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request # type: ignore
from fastapi.responses import JSONResponse, HTMLResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from typing import Dict, List, Any, Optional
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
from exception.custom_exception import DocumentPortalException

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

class FastAPIFileAdapter:
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename
    def get_buffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()


@app.post("/analyze")
async def analyze_document(file:UploadFile = File(...)) -> Any:
    try:
        dh = DocumentHandler()
        save_path=dh.save_pdf(FastAPIFileAdapter(file))
        text = _read_pdf_via_handler(dh, save_path)

        analyzer = DocumentAnalyzer()

        result = analyzer.analyze_document(text)
        return JSONResponse(content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status=500, detail=f"Analysis Failed: {e}")

@app.post("/compare")
async def compare_document(reference: UploadFile=File(...), actual: UploadFile=File(...)) -> Any:
    try:
        dc = DocumentComparator()
        ref_path, actual_path = dc.save_uploaded_files(FastAPIFileAdapter(reference), FastAPIFileAdapter(actual))
        _ = ref_path, actual_path
        combined_text = dc.combine_documents()
        comp = DocumentComparatorLLM()
        df = comp.compare_documents(combined_docs=combined_text)
        return {"rows": df.to_dict(orient="records"), "session_id": dc.session_id}
    
    except HTTPException:
        raise
    except Exception as e:
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
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base=UPLOAD_BASE,
            faiss_base=FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id=session_id or None,
        )
        ci.build_retriever(wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        return {"session_id": ci.session_id, "k": k, "use_session_dirs": use_session_dirs}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status=500, detail=f"Indexing Failed {e}")

@app.post("/chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str] = Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
):
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs is True")
        
        # Prepare FAISS Index
        index_dir = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE
        if not os.path.isdir(index_dir):
            raise HTTPException(status_code=404, detail=f"FAISS Index not found in {FAISS_BASE}")
        
        # Initialize LCEL-style RAG Pipeline
        rag = ConversationalRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_dir)

        # Optional: for now we will pass empty chat history
        response = rag.invoke(question, chat_history=[])

        return {
            "answer": response,
            "session_id": session_id,
            "k": k,
            "engine": "LCEL-RAG",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status=500, detail=f"Chat Query failed : {e}")

