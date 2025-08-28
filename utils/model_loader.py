import os
import sys
# import openai
from dotenv import load_dotenv
from logger import GLOBAL_LOGGER as log
from utils.config_loader import load_config
from exception.custom_exception_archive import DocumentPortalException

from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
# log = CustomLogger().get_logger(__name__)

class ModelLoader:
    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config=load_config()
        log.info("Configuration loaded succesfully...", config_keys=list(self.config.keys()))

    def _validate_env(self):
        required_vars = ['GOOGLE_API_KEY', "GROQ_API_KEY","OPENAI_API_KEY"]
        self.api_keys = {key:os.getenv(key) for key in required_vars}
        self.api_values = [value for key, value in self.api_keys.items()]
        missing = [key for key, value in self.api_keys.items() if not value]
        if missing:
            log.error("Missing environment variables", missing_vars=missing)
            raise DocumentPortalException("Missing environment variables",sys)
        log.info("Environmental variables validated...", available_vars=[k for k in self.api_keys if self.api_keys[k]], api_values=self.api_values)

    def load_embeddings(self):
        try:
            log.info("Loading Embedding Model...")
            model_name=self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise DocumentPortalException("Failed to load embeddings model", sys)
    
    def load_llm(self):
        llm_block=self.config["llm"]
        log.info("Loading LLM models...")

        # Set Default LLM provider in case of any issue
        log.info("LLM block is ", llm_block=llm_block)
        provider_key = os.getenv("LLM_PROVIDER", "google")
        log.info("Provider key is ", provider_key=provider_key)
        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider_key=provider_key)
            raise ValueError(f"Provider '{provider_key}' not found in config")

        llm_config = llm_block[provider_key]
        provider=llm_config.get("provider")
        model_name=llm_config.get("model_name")
        temperature=llm_config.get("temperature", 0.2)
#        max_output_tokens=llm_config.get("max_output_tokens", 2048)

        log.info("Loading LLM: ", provider=provider, model_name=model_name, temperature=temperature) # max_output_tokens=max_output_tokens)

        if provider=="google":
            llm=ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                # max_output_tokens=max_output_tokens
            )
            return llm
        elif provider=="groq":
            llm=ChatGroq(
                model=model_name,
                temperature=temperature,
                # max_output_tokens=max_output_tokens
            )
            return llm
        elif provider=="openai":
            llm=ChatOpenAI(
                model=model_name,
                temperature=temperature,
                # max_output_tokens=max_output_tokens
            )
            return llm
        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")

# if __name__ == "__main__":
#     loader=ModelLoader()

#     #Test embeddings model loading
#     embeddings = loader.load_embeddings()
#     print(f"Embedding model loaded: {embeddings}")

#     #result=embeddings.embed_query("Hello, how are you?")
#     #print(f"Embedded result:{result}")

#     llm = loader.load_llm()
#     print(f"LLM Loaded : {llm}")

#     # Testing results
#     result=llm.invoke("Hello how are you?")
#     print(f"LLM content: {result.content}")
    
