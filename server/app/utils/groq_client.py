import logging
from langchain_groq import ChatGroq
from ..core.config import settings

logger = logging.getLogger(__name__)

def get_groq_client():
    """
    Returns a configured Groq Chat LLM client.
    If the API key or model is missing, logs a clear error message.
    """
    try:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables.")

        llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model=settings.RAG_MODEL,
            temperature=0.1
        )

        logger.info(f"Initialized Groq LLM: {settings.RAG_MODEL}")
        return llm

    except Exception as e:
        logger.error(f"Error initializing Groq client: {e}")
        raise RuntimeError("Failed to initialize Groq LLM. Check your API key or model name.")