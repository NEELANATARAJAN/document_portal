
from __future__ import annotations
import os
import sys
import json
import uuid
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Dict, Any

import fitz # type: ignore
from langchain.schema import Document # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader # type: ignore
from langchain_community.vectorstores import FAISS # type: ignore

from utils.model_loader import ModelLoader
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.file_io import _session_id, save_uploaded_files
from utils.document_ops import load_document, concat_for_analysis, concat_for_compare

SUPPORTED_EXTENSIONS = {'.pdf','.txt','.docx'}

# FAISS Manager (create-or-load)

class FaissManager:
    def __init__(self, index_path: Path, model_loader: Optional[ModelLoader] =None):
        self.index_dir = Path(index_path)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.meta_path = self.index_dir / "ingested_meta.json"
        self._meta : Dict[str: Any] = {"rows": {}}

        if self.meta_path.exists:
            try:
                self._meta = json.loads(self.meta_path.read_text(encoding="utf-8")) or {"rows": {}}
            except Exception:
                self._meta = {"rows": {}}
        
        self.model_loader = model_loader or ModelLoader()
        self.emb = self.model_loader.load_embeddings()
        self.vs : Optional[FAISS] = None

    def _exist(self):
        return (self.index_dir / "index.faiss").exists() or (self.index_dir / "index.pkl").exists() 
    
    @staticmethod
    def _fingerprint(text: str, md: Dict[str, Any]) -> str:
        src = md.get("source") or md.get("file_path")
        rid = md.get("row_id")
        if src is not None:
            return f"{src}:{'' if rid is None else rid}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _save_metadata(self):
        self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")

    def add_documents(self, docs: List[Document]):
        if self.vs is None:
            raise RuntimeError("Call load_or_create before add_documents.")
        new_docs: List[Document] = []

        for d in docs:
            key = self._fingerprint(d.page_content, d.metadata or {})
            if key in self._meta["rows"]:
                continue
            new_docs.append(d)
            self._meta["rows"][key] = True
        if new_docs:
            self.vs.add_documents(new_docs)
            self.vs.save_local(str(self.index_dir))
            self._save_meta()
        return len(new_docs)

    def load_or_create(self, texts: Optional[List[str]]=None, metadatas: Optional[List[dict]]=None):
        if self._exist():
            self.vs = FAISS.load_local(
                str(self.index_dir),
                embedding=self.emb,
                all_dangerous_deserialization=True,
            )
            return self.vs
        if not texts:
            raise DocumentPortalException("No existing FAISS index and no data to create ", sys)
        self.vs = FAISS.from_texts(texts=texts, embedding=self.emb, metadatas=metadatas or [])
        self.vs.save_local(str(self.index_dir))
        return self.vs
    

class ChatIngestor:
    def __init__(self,
                 temp_base: str="data",
                 faiss_base: str="faiss_index",
                 use_session_dirs: bool = True,
                 session_id: Optional[str] = None,
                 ):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.model_loader = ModelLoader()

            self.use_session = use_session_dirs
            self.session_id = session_id or _session_id()

            self.temp_base = Path(temp_base); self.temp_base.mkdir(parents=True, exist_ok=True)
            self.faiss_base = Path(faiss_base); self.faiss_base.mkdir(parents=True, exist_ok=True)

            self.temp_dir = self._resolve(self.temp_base)
            self.faiss_dir = self._resolve(self.faiss_base)

            self.log.info("ChatIngestor Initialized",
                          session_id=self.session_id,
                          temp_dir=str(self.temp_dir),
                          faiss_dir=str(self.faiss_dir),
                          sessionized=self.use_session)
        except Exception as e:
            self.log.error("Failed to initialize the Chat ingestor", error=str(e))
            raise DocumentPortalException("ChatIngestor initialization failed", e) from e

    def _resolve(self, base: Path):
        if self.use_session:
            d = base / self.session_id
            d.mkdir(parents=True, exist_ok=True)
            return d

    def _split(self, docs: List[Document], chunk_size=1000, chunk_overlap=200) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(chunk_overlap=chunk_overlap, chunk_size=chunk_size)
        chunks = splitter.split_documents(docs)
        self.log.info("Document is split", chunk=len(chunks), chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return chunks

    def build_retriever(self,
                        uploaded_files: Iterable,
                        *,
                        chunk_size: int=1000,
                        chunk_overlap: 200,
                        k: int = 5,
                        ):
        try:
            paths = save_uploaded_files(uploaded_files, self.temp_dir)
            docs = load_document(paths)
            if not docs:
                raise ValueError("No valid documents uploaded")
            chunks = self._split(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            fm = FaissManager(self.faiss_dir, self.model_loader)

            texts = [c.page_content for c in chunks]
            metas = [c.metadata for c in chunks]

            try:
                vs = fm.load_or_create(texts=texts, metadatas=metas)
            except Exception:
                vs = fm.load_or_create(texts=texts, metadatas=metas)

            added = fm.add_documents(chunks)
            self.log.info("FAISS Index updated", added=added, index=str(self.faiss_dir))

            return vs.as_retriever(search_type="similarity", search_kwargs={"k":k})
        
        except Exception as e:
            self.log.error("Error building the retriever", error=str(e))
            raise DocumentPortalException("Failed to build the retriever", e) from e



class DocumentHandler:
    def __init__(self, data_dir: Optional[str] = None, session_id: Optional[str] = None):
        self.log = CustomLogger().get_logger(__name__)
        self.data_dir = data_dir or os.getenv("DATA_STORAGE_PATH", os.path.join(os.getcwd(), "data", "document_analysis"))
        self.session_id = session_id
        self.session_path = os.path.join(self.data_dir, self.session_id)
        os.makedirs(self.session_path, exist_ok=True)
        self.log.info("Doc Handler initialized ", session_id=self.session_id, session_path=self.session_path)

    def save_pdf(self, uploaded_file) -> str:
        try:
            filename = os.path.basename(uploaded_file.name)
            if not filename.lower().endswith('.pdf'):
                raise ValueError("Invalid file type only pdf files are allowed")
            save_path = os.path.join(self.session_path, filename)
            with open(save_path, "wb") as f:
                if hasattr(uploaded_file.read()):
                    f.write(uploaded_file.read())
                else:
                    f.write(uploaded_file.getbuffer())
            self.log.info("PDF Saved successfully.", file=filename, save_path=save_path, session_id=self.session_id)
            return save_path
        except Exception as e:
            self.log.error("Failed to upload file", error=str(e), session_id=self.session_id)
            raise DocumentPortalException(f"Failed to upload PDF {filename} {str(e)}", e) from e

    def read_pdf(self, pdf_path: str) -> str:
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text_chunks.append(f"\n-- Page {page_num+1} --\n{page.get_text()}")
            text = "\n".join(text_chunks)
            self.log.info("PDF read successfully.", pdf_path=pdf_path, session_id=self.session_id, pages=len(text_chunks))
            return text
        except Exception as e:
            self.log.error("Failed to read PDF ", error=str(e), pdf_path=pdf_path, session_id=self.session_id)
            raise DocumentPortalException(f"Could not read PDF: {pdf_path}", e) from e

class DocumentComparator:
    def __init__(self, base_dir: str = "data/document_compare", session_id: Optional[str] = None):
        self.log = CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.session_id = session_id
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.log.info("DocumentComparator initialized", session_id=self.session_id, session_path=self.session_path)

    def save_uploaded_files(self, reference_file, actual_file):
        try:
            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name

            for fobj, out in ((reference_file, ref_path), (actual_file, act_path)):
                if not fobj.name.lower().endswith('.pdf'):
                    raise ValueError("Invalid File type only PDF files are allowed.")
                with open(out, "wb") as f:
                    if hasattr(fobj, "read"):
                        f.write(fobj.read())
                    else:
                        f.write(fobj.getbuffer())
            self.log.info("Files saved successfully.", reference=str(ref_path), actual=str(act_path), session_id=self.session_id)
            return ref_path, act_path
        except Exception as e:
            self.log.error("Failed to save uploaded file", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Error saving files", e) from e

    def read_pdf(self, pdf_path: Path) -> str:
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")
                parts=[]
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        parts.append(f"\n-- Page {page_num+1} --\n{text}")
            self.log.info("Files read successfully", file=str(pdf_path), pages=len(parts))
            return "\n".join(parts)
        except Exception as e:
            self.log.error("Failed to read PDF", file=str(pdf_path), error=str(e))
            raise DocumentPortalException(f"Failed to read PDF", e) from e


    def combine_documents(self) -> str:
        try:
            doc_parts = []
            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() == '.pdf':
                    content = self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name}\n{content}")
            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents Combined.", count=len(doc_parts), session=self.session_id)
            return combined_text
        except Exception as e:
            self.log.error("Error combining PDFs", error=str(e), session_id=self.session_id)
            raise DocumentPortalException("Error combining PDFs", e) from e

    def clean_old_sessions(self, keep_latest:int = 3):
        try:
            sessions = sorted([f for f in self.base_dir.iterdir() if f.is_dir()], reverse=True)
            for folder in sessions[keep_latest:]:
                shutil.rmtree(folder, ignore_errors=True)
                self.log.info("Old sessions folder deleted", path=str(folder))  
        except Exception as e:
            self.log.error("Error cleaning the old sessions", error=str(e))
            raise DocumentPortalException("Error cleaning old sessions", e) from e


