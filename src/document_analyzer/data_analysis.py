import os
from utils.model_loader import ModelLoader
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import *

from langchain_core.output_parsers import JSONOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentAnalyzer:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        self.model_loader = ModelLoader()
        self.llm = self.model_loader.load_llm()
        self.output_parser = JSONOutputParser(pydantic_object=Metadata)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.output_parser, llm=self.llm)
        self.prompt = prompt 

    def analyze_document(self):
        pass
