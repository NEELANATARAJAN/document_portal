
from __future__ import annotations
import os
import sys
import json
import uuid
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Dict, Any

import fitz # type: ignore
from langchain.schema import Document # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore
from langchain_community.document_loaders import PyPDFLoader, Doc2txtLoader, TextLoader # type: ignore
from langchain_community.vectorstores import FAISS # type: ignore

from utils.model_loader import ModelLoader
from logger.custom_logger1 import CustomLogger
from exception.custom_exception import DocumentPortalException



class FaissManager:
    def __init__(self):
        pass

    def _exist(self):
        pass
    
    @staticmethod
    def deduplication():
        pass

    def _save_metadata(self):
        pass

    def add_documents(self):
        pass

    def load_or_create(self):
        pass

class DocumentHandler:
    def __init__(self):
        pass

    def save_pdf(self):
        pass

    def read_pdf(self):
        pass

class DocumentComparator:
    def __init__(self):
        pass

    def save_uploaded_files(self):
        pass

    def read_pdf(self):
        pass

    def combine_documents(self):
        pass

    def clean_old_sessions(self):
        pass

class ChatIngestor:
    def __init__(self):
        pass

    def _resolve(self):
        pass

    def _split(self):
        pass

    def build_retriever(self):
        pass

