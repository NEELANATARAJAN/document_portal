import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from datetime import datetime, timezone

class DocumentIngestor:
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.md'} 
    def __init__(self, log, temp_dir:str = "/Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/data/multi_document_chat", faiss_dir: str="faiss_index", session_id:str | None = None):
        try:
            self.log = log
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader(log=self.log)
            self.log.info("Data Ingestion initialized in Multi Document Chat...",
                          temp_base=str(self.temp_dir),
                          faiss_dir=str(self.faiss_dir),
                          session_id=self.session_id,
                          session_temp_dir=str(self.session_temp_dir),
                          session_faiss_dir=str(self.session_faiss_dir)
                          )
        except Exception as e:
            self.log.error(f"Failed to initialize data ingestion in Multidocument chat {e}")
            raise DocumentPortalException("Failed to initialize data ingestion in Multidocument chat", sys)
    
    def ingest_files(self, uploaded_files):
        try:
            documents = []
            print(f"Uploaded files list: {uploaded_files}")

            for uploaded_file in uploaded_files:
                print(f"\nUploaded file extension\n")
                print(f"Path:{Path(uploaded_file.name).suffix.lower()}\n")
                print(f"SUPPORTED EXT: {self.SUPPORTED_EXTENSIONS}")
                ext = Path(uploaded_file.name).suffix.lower()
                if ext not in self.SUPPORTED_EXTENSIONS:
                    self.log.warning(f"Unsupported file format in the uploaded files")
                    continue
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir / unique_filename

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                self.log.info("File saved for ingestion", filename=uploaded_file.name, saved_as=str(temp_path), session_id=self.session_id)

                if ext == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif ext == ".docx":
                    loader = Docx2txtLoader(str(temp_path))
                elif ext == ".txt":
                    loader = TextLoader(str(temp_path), encoding="utf-8")
                else:
                    self.log.warning("Unsupported file encountered", filename=uploaded_file)
                    continue

                docs = loader.load()
                documents.extend(docs)

            if not documents:
                self.log.error(f"No valid document loaded {e}")
                raise DocumentPortalException("No valid document loaded", sys)
            
            self.log.info(f"All documents loaded", total_docs=len(documents), session_id=self.session_id)
            return self._create_retriever(documents)

        except Exception as e:
            self.log.error(f"Error ingesting files in Multidocument chat {e}")
            raise DocumentPortalException("Error ingesting files in Multidocument chat", sys)
    
    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
            chunks = splitter.split_documents(documents)
            self.log.info("Chunks created for the documents", total_chunk=len(chunks), session_id=self.session_id)

            embeddings = self.model_loader.load_embeddings()
            vector_store = FAISS.from_documents(documents=chunks, embedding=embeddings)

            # Save FAISS index under each session folder
            vector_store.save_local(str(self.session_faiss_dir))
            self.log.info("FAISS index saved to disk", path=str(self.session_faiss_dir), session_id=self.session_id)

            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            return retriever
        
        except Exception as e:
            self.log.error(f"Error creating retriever in Multidocument chat {e}")
            raise DocumentPortalException("Error creating retriever in Multidocument chat", sys)
        
