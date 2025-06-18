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

    # Embedding model remains the same - Jina is excellent for this.
    OLLAMA_EMBEDDING_MODEL = "jina/jina-embeddings-v2-base-en"

    # --- START OF CHANGE: UPDATE GENERATION MODELS ---
    # Define the new Qwen3 model as the primary generation model.
    OLLAMA_QWEN3_MODEL_NAME = "qwen3:4b"

    # Set the default Ollama model for the OllamaLLMService to use.
    OLLAMA_DEFAULT_GENERATION_MODEL = OLLAMA_QWEN3_MODEL_NAME
    # --- END OF CHANGE ---

    OLLAMA_GEN_TIMEOUT = int(os.getenv("OLLAMA_GENERATION_TIMEOUT", 120))

    # External Service URLs
    ANN_API_BASE_URL = "https://www.animenewsnetwork.com/encyclopedia/api.php"
    ONE_PIECE_API_BASE_URL = "https://api.api-onepiece.com/v2"
    ANIWATCH_API_BASE_URL = os.getenv("ANIWATCH_API_BASE_URL", "http://localhost:4444")

    # --- LLM Provider Selection ---
    # Update the user-facing names to reflect the new model setup.
    LLM_PROVIDERS = {
        "gemini": "Google Gemini (Cloud)",
        "ollama_qwen3": "Ollama Qwen3 4B (Local)", # Updated to reflect the new model
    }

    # Set the default LLM provider key.
    CURRENT_GENERATION_LLM = os.getenv("DEFAULT_GENERATION_LLM", "ollama_qwen3")

    # Flask App Configuration
    DEBUG = True
    PORT = int(os.getenv("FLASK_PORT", 8001))
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")

    # Vector Store Configuration
    VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vector_db.pkl.gz')

    # Scheduler Configuration
    EMBEDDING_UPDATE_INTERVAL_MINUTES = int(os.getenv("EMBEDDING_UPDATE_INTERVAL_MINUTES", 1440))
