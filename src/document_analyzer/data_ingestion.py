import os
import sys
from frontend import *
import fitz
import uuid
from datetime import datetime
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentHandler:
    def __init__(self,data_dir=None,session_id=None):
        try:

            self.log=CustomLogger().get_logger(__name__)
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

if __name__=="__main__":
    from pathlib import Path
    from io import BytesIO
    
    pdf_path = "/Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/data/document_analysis/NIPS-2017-attention-is-all-you-need-Paper.pdf"
    
    class DummyFiles:
        def __init__(self, file_path):
            self.name = Path(file_path).name
            self.file_path=file_path

        def getbuffer(self):
            return open(self.file_path, "rb").read()
    
    dummy_pdf = DummyFiles(pdf_path)
    handler=DocumentHandler()
    
    try:
        save_path=handler.save_pdf(dummy_pdf)
        print(f"Saved path: {save_path}")

        content = handler.read_pdf(save_path)

        print("PDF Content:")
        print(content[:500])
        print("...")    
    
    except Exception as e:
        print("Error in saving PDF", e)
        raise DocumentPortalException("Error in saving PDF", sys)
    

    





