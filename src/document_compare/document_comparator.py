import os
import sys
from pathlib import Path
import fitz
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from logger.custom_logger1 import CustomLogger
from dotenv import load_dotenv
import pandas as pd
from exception.custom_exception import DocumentPortalException

class DocumentComparatorLLM:
    def __init__(self, log=None):
        self.log = CustomLogger().get_logger(__name__)
        self.model = ModelLoader(log=self.log)
        self.llm = self.model.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY[PromptType.DOCUMENT_COMPARISON.value]
        self.chain = self.prompt | self.llm | self.fixing_parser
        self.log.info("DocumentComparatorLLM initialized with model, parser, prompt and chain.", model=self.llm)

    def compare_documents(self, combined_docs: str) -> pd.DataFrame:
        try:
            inputs = {
                "combined_docs": combined_docs,
                "format_instruction": self.parser.get_format_instructions()
            }
            self.log.info("Starting document comparison with inputs", inputs=inputs)

            response = self.chain.invoke(inputs)
            self.log.info("Document comparison completed successfully.", response_preview=str(response)[:200])

            return self._format_response(response)
        
        except Exception as e:
            self.log.error(f"Error in compare documents: {e}")
            raise DocumentPortalException("Error in compare documents", sys)

    def _format_response(self, response: list[dict]) -> pd.DataFrame:
        try:
            df = pd.DataFrame(response)
            self.log.info("Response formatted into DataFrame successfully.", dataframe=df)
            return df

        except Exception as e:
            self.log.error(f"Error formatting response: {e}")
            raise DocumentPortalException("Error formatting response", sys)

    