import os
import sys
from utils.model_loader import ModelLoader
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import *

from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentAnalyzer:
    def __init__(self, log=None):
        self.log = log
        try:

            self.model_loader = ModelLoader(log=self.log)
            self.llm = self.model_loader.load_llm()
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            self.prompt = prompt

            self.log.info("DocumentAnalyzer successfully initialized.")
        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException("Error initializing DocumentAnalyzer", sys)
        

    def analyze_document(self, document_text:str)->dict:
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            self.log.info("Metadata analysis chain initialized successfully...", chain=chain)

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })

            self.log.info("Metadata extraction successfully completed.", keys=list(response.keys()))
            return response
        
        except Exception as e:
            self.log.error(f"Error analyzing document: {e}")
            raise DocumentPortalException("Error analyzing document", sys)
        
