## Testing document analysis module
#
import os
from pathlib import Path
import sys
from src.document_analyzer.data_ingestion import DocumentHandler
from src.document_analyzer.data_analysis import DocumentAnalyzer
from exception.custom_exception import DocumentPortalException
from logger.custom_logger_archive import CustomLogger

log = CustomLogger().get_logger(__name__)
# PDF_PATH = "/Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/data/document_analysis/sample.pdf"

# class DummyFile:
#     def __init__(self, file_path):
#         self.name=Path(file_path).name
#         self.file_path = file_path
    
#     def getbuffer(self):
#         return open(self.file_path, "rb").read()
    
# if __name__ == "__main__":
#     try:
#         # -------- 1. DATA INGESTION TEST -------- #
#         dummyfile = DummyFile(PDF_PATH)
#         handler = DocumentHandler(log=log)

#         saved_path = handler.save_pdf(dummyfile)
#         print(f"Saved PDF at: {saved_path}")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(text_content)} characters")

#         # --------- 2. DATA ANALYSIS TEST -------- #
#         print("Starting document analysis...")

#         analyzer = DocumentAnalyzer(log=log)
#         metadata_result = analyzer.analyze_document(document_text=text_content)

#         # -------- 3. METADATA ANALYSIS RESULTS -------- #
#         print("Metadata Analysis Results:")
#         for key, value in metadata_result.items():
#             print(f"{key}: {value}")
#         print("Document analysis completed successfully.")

#     except Exception as e:
#         print(f"Error occured during document analysis: {e}")
#         raise DocumentPortalException("Error during document analysis", sys)

## Testing document compare module
#
# import os
# import sys
# import io
# from pathlib import Path
# from src.document_compare.data_ingestion import DocumentComparatorIngestion
# from src.document_compare.document_comparator import DocumentComparatorLLM
# from exception.custom_exception import DocumentPortalException
# from logger.custom_logger1 import CustomLogger
# log = CustomLogger().get_logger(__name__)

# # def load_fake_uploaded_file(file_path: Path):
# #     return io.BytesIO(open(file_path, 'rb').read())

# def test_compare_documents():
#     ref_path = Path("/Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/data/document_compare/Long_Report_V1.pdf")
#     act_path = Path("/Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/data/document_compare/Long_Report_V2.pdf")

#     class FakeUpload:
#         def __init__(self, file_path: Path):
#             self.name = file_path.name
#             self._buffer = file_path.read_bytes()

#         def getbuffer(self):
#             return self._buffer
    
#     log = CustomLogger().get_logger(__name__)
#     comparator = DocumentComparatorIngestion(log=log)
#     ref_upload = FakeUpload(ref_path)
#     act_upload = FakeUpload(act_path)

#     ref_file, act_file = comparator.save_uploaded_file(ref_upload, act_upload)
#     combined_text = comparator.combine_documents()
#     comparator.clean_old_sessions(keep_lastest=3)
    
#     print("\n Combined Text Preview: (First 1000 characters): \n")
#     print(combined_text[:1000])

#     comparator_llm = DocumentComparatorLLM(log=log)
#     comparison_df = comparator_llm.compare_documents(combined_text)

#     print("\n Comparison Results DataFrame: \n")
#     print(comparison_df.head(20))

# if __name__ == "__main__":
#     test_compare_documents()

## Testing Single document chat module
# import sys
# import os
# from pathlib import Path
# from langchain_community.vectorstores import FAISS
# from src.single_document_chat.data_ingestion import SingleDocIngestion
# from src.single_document_chat.retrieval import ConversationalRAG
# from exception.custom_exception import DocumentPortalException
# from utils.model_loader import ModelLoader
# from logger.custom_logger1 import CustomLogger
# import shutil

# log = CustomLogger().get_logger(__name__)

# FAISS_INDEX_PATH = Path("faiss_index")

# def test_conversational_rag_on_pdf(pdf_path: str, question:str):
#     try:
#         model_loader = ModelLoader(log=log)

#         if FAISS_INDEX_PATH.exists():
#             print("Loading existing FAISS index path...")
#             embeddings = model_loader.load_embeddings()
#             vectorstores = FAISS.load_local(folder_path=str(FAISS_INDEX_PATH), embeddings=embeddings, allow_dangerous_deserialization=True)
#             retriever=vectorstores.as_retriever(search_type="similarity", search_kwargs={"k":5})
#         else:
#             print("FAISS index does not exist. Ingesting PDF and creating index ...")
#             with open(pdf_path, "rb") as f:
#                 uploaded_files = [f]
#                 ingestor=SingleDocIngestion(log=log)
#                 retriever=ingestor.ingest_files(uploaded_files=uploaded_files)
#         print("Running Conversational RAG ...")
#         session_id="test_conversational_rag"
#         rag = ConversationalRAG(retriever=retriever, session_id=session_id, log=log)
#         response = rag.invoke(question)
#         print(f"Question: {question}, answer: {response}")

#     except Exception as e:
#         print(f"Test Failed: {str(e)}")

# if __name__ == "__main__":
#     pdf_path="/Users/neeladnatarajan/DSProjects/LLMOps/hw/document_portal/document_portal/data/single_document_chat/NIPS-2017-attention-is-all-you-need-Paper.pdf"
#     question="What is the main topic of the document?"

#     if not Path(pdf_path).exists():
#         print(f"PDF does not exist {pdf_path}")
#         sys.exit(1)
    
#     # Run the conversational RAG 
#     print("Testing conversational RAG")
#     test_conversational_rag_on_pdf(pdf_path, question=question)

    # if os.path.exists(FAISS_INDEX_PATH):
    #     shutil.rmtree(FAISS_INDEX_PATH)
    #     print(f"{FAISS_INDEX_PATH} is removed successfully...")
    # else:
    #     print(f"{FAISS_INDEX_PATH} does not exists.")


## Testing for Multidocument Chat
from src.multi_document_chat.data_ingestion import DocumentIngestor
from src.multi_document_chat.retrieval import ConversationalRAG
import shutil
from pathlib import Path
from logger.custom_logger_archive import CustomLogger
from exception.custom_exception import DocumentPortalException

def test_document_ingestion_rag():
    try:
        # FAISS_INDEX_PATH = Path("faiss_index")
        # if os.path.exists(FAISS_INDEX_PATH):
        #     shutil.rmtree(FAISS_INDEX_PATH)
        #     print(f"{FAISS_INDEX_PATH} is removed successfully...")
        # else:
        #     print(f"{FAISS_INDEX_PATH} does not exists.")
        log = CustomLogger().get_logger(__name__)
        test_files = [
            "data/multi_document_chat/market_analysis_report.docx",
            "data/multi_document_chat/NIPS-2017-attention-is-all-you-need-Paper.pdf",
            "data/multi_document_chat/sample.pdf",
            "data/multi_document_chat/state_of_the_union.txt"
        ]
        print(f"Test files location:\n{test_files}")

        uploaded_files = []
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
            else:
                print(f"File does not exists {file_path}")
        
        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)
        
        ingestor = DocumentIngestor(log=log)

        ingested_retriever = ingestor.ingest_files(uploaded_files=uploaded_files)

        for f in uploaded_files:
            f.close()
        
        session_id = "test_multidoc_chat"
        rag = ConversationalRAG(session_id=session_id, retriever=ingested_retriever, log=log)
        question="What is attention is all you need paper about?"
        answer = rag.invoke(question)
        print(f"\nQuestion: {question}, \n Answer: {answer}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

test_document_ingestion_rag()
