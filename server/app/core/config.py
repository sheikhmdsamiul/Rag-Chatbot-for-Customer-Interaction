import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    #External APIs
    DUMMYJSON_API_URL: str = "https://dummyjson.com/products"

    #GROQ and Model Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    RAG_MODEL: str = os.getenv("RAG_MODEL", "llama-3.3-70b-versatile")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

    #App Configuration
    APP_NAME: str = "Product Assistant API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


    #Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

#Global instance
settings = Settings()