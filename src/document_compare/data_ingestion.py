import sys
from pathlib import Path
import fitz
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException
from datetime import datetime, timezone
import uuid

class DocumentComparatorIngestion:
    def __init__(self, base_dir: str="data/document_compare", log=None, session_id=None):
        self.log = log or CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.log.info("DocumentComparatorIngestion initialized", session_path=str(self.session_path))


    def clean_old_sessions(self, keep_lastest: int=3):
        try:
            session_folders = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse=True
            )
            for folder in session_folders[keep_lastest:]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                self.log.info(f"Deleted old session folder", path=str(folder))

        except Exception as e:
            self.log.error(f"Error deleting existing files in DocumentComparator: {e}")
            raise DocumentPortalException("Error deleting existing files in DocumentComparator", sys)

    def save_uploaded_file(self, reference_file: Path, actual_file: Path):        
        try:
            # self.delete_existing_files()
            # self.log.info(f"Existing files deleted successfully in DocumentComparator")

            ref_path = self.session_path / reference_file.name
            act_path = self.session_path / actual_file.name

            if not reference_file.name.lower().endswith('.pdf') or not actual_file.name.lower().endswith('.pdf'):
                raise ValueError("Only PDF files are allowed for comparison.")
            
            with open(ref_path, 'wb') as f:
                f.write(reference_file.getbuffer())
            
            with open(act_path, 'wb') as f:
                f.write(actual_file.getbuffer())
            
            self.log.info("Files saved successfully in DocumentComparator", reference=str(ref_path), actual=str(act_path))
            return ref_path, act_path

        except Exception as e:
            self.log.error(f"Error saving uploaded file in DocumentComparator: {e}")
            raise DocumentPortalException("Error saving uploaded file in DocumentComparator", sys)

    def read_pdf(self, pdf_path: Path):
        
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted and cannot be read: {pdf_path.name}")
                
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        all_text.append(f"\n--- Page {page_num+1} ---\n {text}")

            self.log.info("PDF read successfully", file=pdf_path.name, pages=len(all_text))
            return "\n".join(all_text)            

        except Exception as e:
            self.log.error(f"Error reading PDF File in DocumentComparator: {e}")
            raise DocumentPortalException("Error readiing PDF File in DocumentComparator", sys)
    
    def combine_documents(self):
        try:
            # content_dict = {}
            doc_parts = []

            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() == ".pdf":
                    content = self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name} \n {content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined successfully in DocumentComparator", length=len(combined_text), session_id=self.session_id)
            return combined_text


        except Exception as e:
            self.log.error(f"Error combining documents in DocumentComparator: {e}")
            raise DocumentPortalException("Error combining documents in DocumentComparator", sys)
        