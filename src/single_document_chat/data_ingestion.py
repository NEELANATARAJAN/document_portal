import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from datetime import datetime, timezone

class SingleDocIngestion:
    def __init__(self,log, base_dir: str = "data/single_document_chat", faiss_dir:str = "faiss_index"):
        try:
            self.log = log
            self.log.info("SingleDocument Chat initialization invoked")
            self.base_dir = Path(base_dir)
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True) 
            self.model = ModelLoader(log=log)
            self.log.info("SingleDocument Ingestion initialized", temp_path=self.base_dir, faiss_path=self.faiss_dir)
        
        except Exception as e:
            self.log.error(f"Error initializing SingleDocIngestion: {e}")
            raise DocumentPortalException("Error initializing SingleDocIngestion", sys)
        

    def ingest_files(self, uploaded_files):
        try:
            documents = []
            for upload_file in uploaded_files:
                unique_filename = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                temp_path = self.base_dir / unique_filename

                with open(temp_path, "wb") as f:
                    f.write(upload_file.read())
                
                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
            self.log.info(f"Uploaded files saved in the location {temp_path}", count=len(documents))
            
            return self._create_retriever(documents)

        except Exception as e:
            self.log.error(f"Error in ingest files in single document ingestion {e}")
            raise DocumentPortalException("Error in ingest files in single document ingestion", sys)
    
    def _create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
            chunks = splitter.split_documents(documents)
            self.log.info(f"Document is split into chunks of length {len(chunks)}")

            embeddings = self.model.load_embeddings()
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)

            # Save FAISS Index
            vectorstore.save_local(str(self.faiss_dir))
            self.log.info(f"FAISS index created and saved", faiss_path=self.faiss_dir)

            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k":5})
            self.log.info("Retriever created successfully", retriever_type=str(type(retriever)))
            return retriever

        except Exception as e:
            self.log.error(f"Error in creating retriever in single document ingestion {e}")
            raise DocumentPortalException("Error in creating retriever in single document ingestion", sys)
        

