# logger/__init__.py
from .custom_logger import CustomLogger
GLOBAL_LOGGER = CustomLogger().get_logger("document_portal")