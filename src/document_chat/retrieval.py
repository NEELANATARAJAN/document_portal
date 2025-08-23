import sys
import os

from operator import itemgetter
from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger import GLOBAL_LOGGER as log
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, session_id:Optional[str], retriever=None):
        try:
            self.session_id = session_id
            log.info(f"Retriever sent from api is {retriever}")
            self.llm = self._load_llm()
            self.contextualize_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUAL_QUESTION.value]
            self.qa_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUAL_QA.value]
            self.retriever = retriever
            self.chain = None
            if self.retriever is not None:
                self._build_lcel_chain()

            log.info("ConversationRAG initialized", session_id=self.session_id)
        except Exception as e:
            log.error(f"Failed to initialize ConversationalRAG {e}")
            raise DocumentPortalException("Failed to initialize ConversationalRAG ", sys)

    def load_retriever_from_faiss(
            self, 
            index_path:str, 
            k: int = 5, 
            index_name:str = "index", 
            search_type: str = "similarity",
            search_kwargs: Optional[Dict[str, Any]] = None):
        try:
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            embeddings = ModelLoader().load_embeddings()
            vector_store = FAISS.load_local(
                index_path,
                embeddings,
                index_name=index_name,
                allow_dangerous_deserialization=True,
            )
            if search_kwargs is None:
                search_kwargs = {'k': k}

            self.retriever = vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
            self._build_lcel_chain()

            log.info("FAISS retriever loaded successfully", 
                     index_path=index_path, 
                     index_name=index_name, 
                     k=k,
                     session_id=self.session_id)
            return self.retriever

        except Exception as e:
            log.error(f"Failed to load retriever {e}")
            raise DocumentPortalException("Failed to load retriever", sys)

    def invoke(self, user_input:str, chat_history:Optional[List[BaseMessage]]=None) -> str:
        try:
            if self.chain is None:
                raise DocumentPortalException(
                    "RAG Chain not initialized. Call load_retriever_from_faiss() before invoke()", sys
                )
            
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history}
            answer = self.chain.invoke(payload)
            if not answer:
                log.warning("No answer generated", session_id=self.session_id, user_input=user_input)
                return "No answer generated"
            log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
            return answer

        except Exception as e:
            log.error(f"Error invoking ConversationRAG {e}")
            raise DocumentPortalException("Error invoking ConversationRAG", sys)

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM cannot be loaded...")
            log.info("LLM loaded successfully...", session_id=self.session_id)
            return llm
        
        except Exception as e:
            log.error(f"Error loading LLM in ConversationalRAG {e}")
            raise DocumentPortalException("Error loading LLM in ConversationalRAG", sys)

    @staticmethod
    def _format_docs(docs):
        try:
            return "\n\n".join(d.page_content for d in docs)
        
        except Exception as e:
            raise DocumentPortalException("Error formatting documents in ConversationalRAG", sys)
    
    def _build_lcel_chain(self):
        try:
            if self.retriever is None:
                raise DocumentPortalException("No retriever set before building chain", sys)
            
            question_rewriter = (
                {"input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            retrieve_docs = question_rewriter | self.retriever | self._format_docs

            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history"),
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )
            log.info("LCEL chain built successfully", session_id=self.session_id)

        except Exception as e:
            log.error(f"Error building LCEL chain in ConversationalRAG {e}")
            raise DocumentPortalException("Error building LCEL chain in ConversationalRAG", sys)

