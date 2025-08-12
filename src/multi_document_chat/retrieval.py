import sys
import os

from operator import itemgetter
from typing import List, Optional
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger1 import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, log, session_id:str, retriever=None):
        try:
            self.log = log
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextualize_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUAL_QUESTION.value]
            self.qa_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUAL_QA.value]
            if retriever is None:
                self.log.error("Retriever cannot be None")
                raise DocumentPortalException("Retriever cannot be None")
            self.retriever = retriever
            self._build_lcel_chain()
            self.log.info("ConversationRAG initialized", session_id=self.session_id)
        except Exception as e:
            self.log.error(f"Failed to initialize ConversationalRAG {e}")
            raise DocumentPortalException("Failed to initialize ConversationalRAG ", sys)

    def load_retriever_from_faiss(self, index_path:str):
        try:
            embeddings = ModelLoader(log=self.log).load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            vector_store = FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True,
            )

            self.retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={'k': 5})
            self.log.info("FAISS retriever loaded successfully", index_path=index_path, session_id=self.session_id)
            return self.retriever

        except Exception as e:
            self.log.error(f"Failed to load retriever {e}")
            raise DocumentPortalException("Failed to load retriever", sys)

    def invoke(self, user_input:str, chat_history:Optional[List[BaseMessage]]=None) -> str:
        try:
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history}
            answer = self.chain.invoke(payload)
            if not answer:
                self.log.warning("No answer generated", session_id=self.session_id, user_input=user_input)
                return "No answer"
            self.log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_preview=answer[:150])
            return answer

        except Exception as e:
            self.log.error(f"Error invoking ConversationRAG {e}")
            raise DocumentPortalException("Error invoking ConversationRAG", sys)

    def _load_llm(self):
        try:
            llm = ModelLoader(log=self.log).load_llm()
            if not llm:
                raise ValueError("LLM cannot be loaded...")
            self.log.info("LLM loaded successfully...", session_id=self.session_id)
            return llm
        
        except Exception as e:
            self.log.error(f"Error loading LLM in ConversationalRAG {e}")
            raise DocumentPortalException("Error loading LLM in ConversationalRAG", sys)

    @staticmethod
    def _format_docs(docs):
        try:
            return "\n\n".join(d.page_content for d in docs)
        
        except Exception as e:
            raise DocumentPortalException("Error formatting documents in ConversationalRAG", sys)
    
    def _build_lcel_chain(self):
        try:
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
            self.log.info("LCEL chain built successfully", session_id=self.session_id)

        except Exception as e:
            self.log.error(f"Error building LCEL chain in ConversationalRAG {e}")
            raise DocumentPortalException("Error building LCEL chain in ConversationalRAG", sys)

