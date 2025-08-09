import uuid
from pathlib import Path
import sys
from langchain_core.documents import PyPDFLoader
from langchain_text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader

class SingleDocIngestion:
    def __init__(self):
        try:
            self.log = CustomLogger.get_logger(__name__)
        
        except Exception as e:
            self.log.error(f"Error initializing SingleDocIngestion: {e}")
            raise DocumentPortalException("Error initializing SingleDocIngestion", sys)
    
    def ingest_files(self):
        try:
            pass

        except Exception in e:
            self.log.error(f"Error in ingest files in single document ingestion {e}")
            raise DocumentPortalException("Error in ingest files in single document ingestion", sys)
    
    def _create_retriever(self):
        try:
            pass

        except Exception as e:
            self.log.error(f"Error in creating retriever in single document ingestion {e}")
            raise DocumentPortalException("Error in creating retriever in single document ingestion", sys)
        

