import os
import sys
from utils.model_loader import ModelLoader
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY

from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentAnalyzer:
    """
    Analyzes document using a pre-trained LLM model.
    Automatically logs all actions and supports session-based organization.
    """
    def __init__(self):
        try:
            self.model_loader = ModelLoader()
            self.llm = self.model_loader.load_llm()
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            self.prompt = PROMPT_REGISTRY[PromptType.DOCUMENT_ANALYSIS.value]

            log.info("DocumentAnalyzer successfully initialized.")
        except Exception as e:
            log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException("Error initializing DocumentAnalyzer", sys)
        

    def analyze_document(self, document_text:str)->dict:
        """
        Analyze a document's text and extract structured metadata & summary
        """
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            log.info("Metadata analysis chain initialized successfully...", chain=chain)

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })

            log.info("Metadata extraction successfully completed.", keys=list(response.keys()))
            return response
        
        except Exception as e:
            log.error(f"Error analyzing document: {e}")
            raise DocumentPortalException("Error analyzing document", sys)
        
