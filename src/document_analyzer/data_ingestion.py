import os
import sys
from frontend import *
import fitz
import uuid
from datetime import datetime
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentHandler:
    def __init__(self,data_dir=None,session_id=None, log=None):
        try:

            self.log=log 
            self.data_dir=data_dir or os.getenv(
                "DATA_STORAGE_PATH", 
                os.path.join(os.getcwd(),"data","document_analysis"))
            self.session_id=session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            self.session_path=os.path.join(self.data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)

            self.log.info("PDFHandler initialized...", session_id=self.session_id, session_path=self.session_path)
 
        except Exception as e:
            self.log.error(f"Error initializing DocumentHandler:{e}")
            raise DocumentPortalException("Error initializing DocumentHandler ", sys)

    def save_pdf(self, uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)
            self.log.info("Called pdf save method", uploaded_file=uploaded_file, filename=uploaded_file.name)
            
            if not filename.lower().endswith('.pdf'):
                raise DocumentPortalException("Invalid file type. Only PDF files are allowed.", sys)
            
            save_path = os.path.join(self.session_path, filename)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            self.log.info("PDF saved successfully", file=filename, save_path=save_path, session_id=self.session_id)
            return save_path

        except Exception as e:
            self.log.error("Error saving PDF : {e}")
            raise DocumentPortalException("Error saving PDF", sys)
    
    def read_pdf(self, pdf_path):
        try:
            text_chunks=[]
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text_chunks.append(f"-----\n page {page_num} ----\n {page.get_text()} ")
            text = "\n".join(text_chunks)
            if not text:
                raise DocumentPortalException("PDF is empty or could not be read.", sys)
            
            self.log.info("PDF read successfully", pdf_path=pdf_path, session_id=self.session_id)
            return text

        except Exception as e:
            self.log.error("Error while reading the PDF: {e}")
            raise DocumentPortalException("Error while reading the PDF", sys)






