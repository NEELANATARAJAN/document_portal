# tests/test_unit_cases.py

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from api.main import app # document-portal FastAPI entrypoint
from src.document_compare.document_comparator import DocumentComparatorLLM
from PyPDF2 import PdfWriter
from io import BytesIO
import os

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

# def test_analyze_documents():
#     mock_file = create_mock_pdf_file()
#     files_payload = {
#         "file": ("document.pdf", mock_file.read(), "application/pdf")
#         }
#     response = client.post("/analyze", files=files_payload)
#     assert response.status_code == 200



# def test_analyze_document():
#     file_name="market_analysis.pdf"
#     file_path = os.path.join("/Users/neeladnatarajan/Documents/")

