from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
from fastapi import UploadFile
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException
SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx'}

def load_documents(paths: Iterable[Path]) -> List[Document]:
    docs: List[Document] = []
    try:
        for p in paths:
            ext = p.suffix.lower()
            if ext == ".pdf":
                loader = PyPDFLoader(str(p))
            elif ext == ".txt":
                loader = TextLoader(str(p), encoding="utf-8")
            elif ext == ".docx":
                loader = Docx2txtLoader(str(p))
            else:
                log.warning("Unsupported extension file skipped.", path=str(p))
                continue
            docs.extend(loader.load())
        log.info("Documents loaded successfully", count=len(docs))
        return docs
    except Exception as e:
        log.error("Failed to load documents", error=str(e))
        raise DocumentPortalException("Error loading documents", e) from e

def concat_for_analysis(docs: List[Document]) -> List[Document]:
    parts=[]
    for d in docs:
        src = d.metadata.get("source") or d.metadata.get("file_path") or "unknown"
        parts.append(f"\n-- SOURCE: {src} --\n{d.page_content}")
    return "\n".join(parts)

def concat_for_compare(ref_docs: List[Document], act_docs: List[Document]) -> str:
    left = concat_for_analysis(ref_docs)
    right = concat_for_analysis(act_docs)
    return f"<<REFERENCE_DOCUMENTS>>\n{left}\n\n<<ACTUAL_DOCUMENTS>>\n{right}"

def read_pdf_via_handler(handler, path: str) -> str:
    try:
        if hasattr(handler, 'read_pdf'):
            return handler.read_pdf(path)
        if hasattr(handler, "read_"):
            return handler.read_(path)
    except Exception as e:
        raise RuntimeError("Document Handler has neigther read nor read_ method.")
    