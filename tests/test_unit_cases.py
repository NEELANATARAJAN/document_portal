# tests/test_unit_cases.py

import pytest
import fitz  # PyMuPDF
from pathlib import Path
from fastapi.testclient import TestClient
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request 
from api.main import app # document-portal FastAPI entrypoint
from src.document_compare.document_comparator import DocumentComparatorLLM
from PyPDF2 import PdfWriter
from io import BytesIO
import os
from typing import List
from src.document_chat.retrieval import ConversationalRAG
from utils.document_ops import read_pdf_via_handler, FastAPIFileAdapter
from src.document_ingestion.data_ingestion import ChatIngestor
from starlette.datastructures import UploadFile
from io import BytesIO

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

BASE_DIR = Path(__file__).resolve().parent.parent

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "Document Portal" in response.text

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert "document-portal" in response.text

# def create_mock_pdf_file():
#     """Creates a simple in-memory PDF file for testing."""
#     # A simple, valid PDF header as a byte string
#     pdf_header = b"market_analysis\n"
#     # Some mock content
#     local_file = Path("./market_analysis.pdf")
#     with open (local_file, "rb") as f:
#         pdf_content = f.read()
    
#     # Return a BytesIO object which acts like a file
#     return BytesIO(pdf_content)

def test_analyze_documents():
#    test_file_path = "market_analysis.pdf"
    with open(str(BASE_DIR, "tests/market_analysis.pdf"),"rb") as pdf_file:
        response = client.post("/analyze", files={"file": ("market_analysis.pdf", pdf_file, "application/pdf")})
    assert response.status_code == 200
    data = response.json()
    print("Response JSON:", data)
    assert "Summary" in data
    assert isinstance(data["Summary"], List)
    assert len(data["Summary"]) > 0


def test_compare_documents():
    ref_path = str(BASE_DIR, "/tests/Long_Report_V1.pdf")
    act_path = str(BASE_DIR,"/tests/Long_Report_V2.pdf")
    with open(ref_path,"rb") as ref_file, open(act_path,"rb") as act_file:
        response = client.post("/compare", files={"reference": ("Long_Report_V1.pdf", ref_file, "application/pdf"), "actual": ("Long_Report_V2.pdf", act_file, "application/pdf")})
    assert response.status_code == 200
    data = response.json()
    print("\n\nResponse JSON:", data)
    assert "rows" in data
    # assert isinstance(data["Summary"], List)
    # assert len(data["Summary"]) > 0


# def test_analyze_document():
#     file_name="market_analysis.pdf"
#     file_path = os.path.join("/Users/neeladnatarajan/Documents/")

FAISS_BASE = Path("faiss_index")
UPLOAD_BASE = Path("data/testing")
FAISS_INDEX_NAME = "index"
use_session_dirs=False
session_id="testsession"
chunk_size=1000
chunk_overlap=300
k=5

def test_chat_ingestor():
    files = str(BASE_DIR,"/tests/market_analysis.pdf")
    with open(files,"rb") as f:
        file_content = f.read()

    f_bytes = BytesIO(file_content)
    chat_files = UploadFile(filename="market_analysis.pdf", file=f_bytes)
    chat_files.__dict__["content_type"] = "application/pdf"

    wrapped = FastAPIFileAdapter(chat_files)
    ci = ChatIngestor(
        temp_base=UPLOAD_BASE,
        faiss_base=FAISS_BASE,
        use_session_dirs=use_session_dirs,
        session_id=session_id or None,
    )
    retriever = ci.build_retriever([wrapped], chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
    print("\n\nType of retriever:", type(retriever))
    assert type(retriever).__name__ == "VectorStoreRetriever"
    assert retriever.search_type == "similarity"
    assert retriever.search_kwargs["k"] == k

def test_chat_query():
    files = str(BASE_DIR,"/tests/market_analysis.pdf")
    with open(files,"rb") as f:
        file_content = f.read()

    f_bytes = BytesIO(file_content)

    files = [("files",("market_analysis.pdf", f_bytes, "application/pdf"))]

    params = {
        "session_id": "/data/testing/20250705",
        "use_session_dirs": True,
        "chunk_size": 1000,
        "chunk_overlap": 300,
        "k": 5
    }
    
    response_index = client.post("/chat/index/", files=files, params = params)

    index_data = response_index.json()
    print("\n\nResponse JSON:", index_data)
    assert response_index.status_code == 200
    assert "session_id" in index_data
    # assert data["session_id"] is not None
    assert index_data["k"] == 5
    
    session_ids = index_data["session_id"]
    print(f"\n\nsession_id {session_ids}")
    
    query="What is the market analysis report about?"
    print("\n\nIndex session id:", index_data['session_id'])
    response = client.post("/chat/query/", 
                           data={"question": query, "session_id": session_ids, "use_session_dirs": True, "k": 5})
    
    data = response.json()
    print("\n\nResponse JSON:", data)

    assert response.status_code == 200
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0
    assert data['engine'] == "LCEL-RAG"

@pytest.mark.asyncio
async def test_chat_query_with_deepeval():
    # --- Load test file ---
    file_path = str(BASE_DIR,"/tests/market_analysis.pdf")
    with open(file_path, "rb") as f:
        file_content = f.read()

    f_bytes = BytesIO(file_content)
    files = [("files", ("market_analysis.pdf", f_bytes, "application/pdf"))]

    # --- Indexing params ---
    params = {
        "session_id": "session-20250705",
        "use_session_dirs": True,
        "chunk_size": 1000,
        "chunk_overlap": 300,
        "k": 5
    }

    # --- Index the document ---
    response_index = client.post("/chat/index/", files=files, params=params)
    assert response_index.status_code == 200
    index_data = response_index.json()
    session_id = index_data["session_id"]
    assert session_id

    # --- Chat query ---
    question = "Which company is the highest grossing in revenue?"
    response_chat = client.post("/chat/query/", data={
        "question": question,
        "session_id": session_id,
        "use_session_dirs": True,
        "k": 5
    })

    assert response_chat.status_code == 200
    data = response_chat.json()
    answer = data.get("answer")

    # --- Validate response format ---
    assert answer
    assert isinstance(answer, str)
    assert data["engine"] == "LCEL-RAG"

    # --- Retrieved context (simplified mock example; ideally load from doc directly) ---
    
    def extract_text_from_pdf(pdf_bytes):
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = []
        for i in range(doc.page_count):
            text = doc.load_page(i).get_text()
            if text.strip():
                pages.append(text)
        return pages
    
    context = extract_text_from_pdf(file_content)
    print("\n\nContext for evaluation:", context[:100])

    os.environ["DEEPEVAL_OPENAI_MODEL"] = "gpt-3.5-turbo"
    
    # --- DeepEval test case ---
    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        retrieval_context=context
    )

    # --- Run evaluation ---
    evaluate(
        test_cases=[test_case],
        metrics=[
            AnswerRelevancyMetric(threshold=0.8),
            FaithfulnessMetric(threshold=0.8)
        ]
    )
    # print("\n---- Deep Eval ----\n")
    # for metric in test_case.metrics:
    #     print(f"{metric.__class__.__name__}:")
    #     print(f" ✅ Passed: {metric.passed}")
    #     print(f" 📈 Score : {metric.score:.2f}")
    #     if hasattr(metric, "explanation") and metric.explanation:
    #         print(f" 📝 Explanation: {metric.explanation}")
    #     print("\n")
