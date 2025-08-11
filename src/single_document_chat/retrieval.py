# Importing necessary libraries and modules
import os
import sys
from dotenv import load_dotenv
import streamlit as st
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory # type : ignore
from langchain_community.vectorstores import FAISS # type : ignore
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils.model_loader import ModelLoader
from exception.custom_exception1 import DocumentPortalException
from logger.custom_logger1 import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, session_id: str, retriever, log):
            self.log = log
            self.session_id = session_id
            self.retriever = retriever

            try:
                 self.llm = self._load_llm(log=self.log, session_id=self.session_id)
                 self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUAL_QUESTION.value]
                 self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUAL_QA.value]
                 self.history_aware_retriever = create_history_aware_retriever(
                     self.llm, self.retriever, self.contextualize_prompt
                 )
                 self.log.info("Created history aware retriever", session_id=self.session_id)
                 
                 self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
                 self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)
                 self.log.info("Created RAG Chain", session_id=self.session_id)

                 self.chain = RunnableWithMessageHistory(
                     self.rag_chain,
                     self._get_session_history,
                     input_messages_key="input",
                     history_messages_key="chat_history",
                     output_messages_key="answer"
                     )
                 self.log.info("Created RunnableWithMessageHistory", session_id=self.session_id)

            except Exception as e:
                self.log.error(f"Error initializing SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
                raise DocumentPortalException("Error initializing SingleDoc ConversationalRAG", sys)
    
    def _load_llm(self, session_id: str, log):
        try:
            llm = ModelLoader(log=self.log).load_llm()
            self.log.info("LLM loaded successfully", class_name=llm.__class__.__name__)
            return llm
        
        except Exception as e:
            self.log.error(f"Error loading LLM in SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
            raise DocumentPortalException("Error loading LLM in SingleDoc ConversationalRAG", sys)

    def _get_session_history(self, session_id):
        try:
            if "store" not in st.session_state:
                st.session_state.store = {}

            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
                self.log.info("New chat session history created", session_id=session_id)

            return st.session_state.store[session_id]
        
        except Exception as e:
            self.log.error(f"Error getting session history in SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
            raise DocumentPortalException("Error getting session history in SingleDoc ConversationalRAG", sys)

    def load_retriever_from_faiss(self, index_path:str, log):
        try:
            embeddings = ModelLoader(log=self.log).load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            vectorstore = FAISS.load_local(index_path, embeddings)
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("Retriever loaded successfully", index_path=index_path)
            return retriever
            
        except Exception as e:
            self.log.error(f"Error loading retriever from FAISS in SingleDoc ConversationalRAG: {e}", session_id=self.session_id)
            raise DocumentPortalException("Error loading retriever from FAISS in SingleDoc ConversationalRAG", sys) 
    
    def invoke(self, user_input: str):
        try:
            response = self.chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": self.session_id}}
            )
            answer =  response.get("answer", "No answer.")
            if not answer:
                self.log.warning("Empty answer received", session_id=self.session_id)
            
            self.log.info("RAG Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_previous=answer[:150])
            return answer
        
        except Exception as e:
            self.log.error(f"Error invoking SingleDoc ConversationalRAG {e}", session_id=self.session_id)
            raise DocumentPortalException("Error invoking SingleDoc ConversationalRAG", sys)
    


