# Importing necessary libraries and modules
import os
import sys
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory # type : ignore
from langchain_community.vectorstores import FAISS # type : ignore
from langchani_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from exception.custom_exception1 import DocumentPortalException
from logger.custom_logger1 import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, session_id: str, retriever)-> None:
        try:
            self.log = CustomLogger.get_logger(__name__)
            self.session_id = session_id
        except Exception as e:
            self.log.error(f"Error initializing SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
            raise DocumentPortalException("Error initializing SingleDoc ConversationalRAG", sys)
    
    def _load_llm(self, session_id: str):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error loading LLM in SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
            raise DocumentPortalException("Error loading LLM in SingleDoc ConversationalRAG", sys)

    def _get_session_history(self, session_id):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error getting session history in SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
            raise DocumentPortalException("Error getting session history in SingleDoc ConversationalRAG", sys)

    def _load_retriever_from_faiss(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error loading retriever from FAISS in SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
            raise DocumentPortalException("Error loading retriever from FAISS in SingleDoc ConversationalRAG", sys) 
    
    def invoke(self, session_id):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error invoking SingleDoc ConversationalRAG {e}", session_id=self.session_id)
            raise DocumentPortalException("Error invoking SingleDoc ConversationalRAG", sys)
    


