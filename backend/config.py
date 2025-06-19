# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file at the very start
load_dotenv()

class Config:
    # --- API Keys & External Service URLs ---
    GEMINI_API_KEY = os.getenv("GEMINI_KEY")

    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # --- START OF DEFINITIVE FIX: Restored correct model name ---
    # Embedding model for converting text to vectors.
    OLLAMA_EMBEDDING_MODEL = "snowflake-arctic-embed2:latest"
    # --- END OF DEFINITIVE FIX ---

    # Define your specific generation model name here.
    OLLAMA_QWEN3_MODEL_NAME = "qwen3:4b"

    # Set the default Ollama model for all services to use.
    OLLAMA_DEFAULT_GENERATION_MODEL = OLLAMA_QWEN3_MODEL_NAME

    OLLAMA_GEN_TIMEOUT = int(os.getenv("OLLAMA_GENERATION_TIMEOUT", 120))

    # External Service URLs
    ANN_API_BASE_URL = "https://www.animenewsnetwork.com/encyclopedia/api.php"
    ONE_PIECE_API_BASE_URL = "https://api.api-onepiece.com/v2"
    ANIWATCH_API_BASE_URL = os.getenv("ANIWATCH_API_BASE_URL", "http://localhost:4444")

    # The provider list now accurately reflects your available models.
    LLM_PROVIDERS = {
        "gemini": "Google Gemini (Cloud)",
        "ollama_qwen3": "Ollama Qwen3 4B (Local)", # Simplified to one local provider
    }

    # Set the default LLM provider key to your Qwen3 model.
    CURRENT_GENERATION_LLM = os.getenv("DEFAULT_GENERATION_LLM", "ollama_qwen3")

    # Flask App Configuration
    DEBUG = True
    PORT = int(os.getenv("FLASK_PORT", 8001))
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")

    # Vector Store Configuration
    VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vector_db.pkl.gz')

    # Scheduler Configuration
    EMBEDDING_UPDATE_INTERVAL_MINUTES = int(os.getenv("EMBEDDING_UPDATE_INTERVAL_MINUTES", 1440))
