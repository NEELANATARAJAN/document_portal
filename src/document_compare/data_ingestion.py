import sys
from pathlib import Path
import fitz
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentComparatorIngestion:
    def __init__(self, base_dir: str="data/document_compare", log=None):
        self.log = log or CustomLogger().get_logger(__name__)
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def delete_existing_files(self):
        try:
            if self.base_dir.exists() and self.base_dir.is_dir():
                for file in self.base_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                        self.log.info(f"Deleted file", path=str(file))
                self.log.info("Director cleaned successfully in DocumentComparator", directory=str(self.base_dir))

        except Exception as e:
            self.log.error(f"Error deleting existing files in DocumentComparator: {e}")
            raise DocumentPortalException("Error deleting existing files in DocumentComparator", sys)

    def save_uploaded_file(self, reference_file: Path, actual_file: Path):        
        try:
            self.delete_existing_files()
            self.log.info(f"Existing files deleted successfully in DocumentComparator")

            ref_path = self.base_dir / reference_file.name
            act_path = self.base_dir / actual_file.name

            if not reference_file.name.endswith('.pdf') or not actual_file.name.endswith('.pdf'):
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
                    raise ValueError("PDF is encrypted and cannot be read: {pdf_path.name}")
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        all_text.append(f"\n--- Page {page_num+1} ---\n {text.strip()}")
            self.log.info(f"PDF read successfully {pdf_path.name}, pages={len(all_text)}")
            return "\n".join(all_text)            

        except Exception as e:
            self.log.error(f"Error reading PDF File in DocumentComparator: {e}")
            raise DocumentPortalException("Error readiing PDF File in DocumentComparator", sys)
    
    def combine_documents(self):
        try:
            content_dict = {}
            doc_parts = []

            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix.lower() == ".pdf":
                    content_dict[filename.name] = self.read_pdf(filename)
            
            for filename, content in content_dict.items():
                doc_parts.append(f"Document: {filename}\n{content}")

            combined_text = "\n\n".join(doc_parts)
            self.log.info("Documents combined successfully in DocumentComparator", length=len(combined_text))
            return combined_text


        except Exception as e:
            self.log.error(f"Error combining documents in DocumentComparator: {e}")
            raise DocumentPortalException("Error combining documents in DocumentComparator", sys)
        