# backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file at the very start
# This ensures that os.getenv() calls below can find the values
load_dotenv()

class Config:
    # --- API Keys & External Service URLs ---
    GEMINI_API_KEY = os.getenv("GEMINI_KEY")

    # Ollama Configuration
    # Use environment variable for base URL with a common default
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL = "all-minilm:latest" # Internal, never exposed to user

    # Define specific Ollama models available for generation
    # The new anime model you pulled:
    OLLAMA_ANIME_MODEL_NAME = "sc0v0ne/xeroxvaldo_sharopildo:latest"
    # Your existing qwen2.5 model:
    OLLAMA_QWEN_MODEL_NAME = "qwen2.5:3b"

    # Set the default Ollama model for the OllamaLLMService to use
    # This will be the anime model you want as the primary
    OLLAMA_DEFAULT_GENERATION_MODEL = OLLAMA_ANIME_MODEL_NAME
    # Timeout for Ollama LLM generation in seconds
    OLLAMA_GEN_TIMEOUT = int(os.getenv("OLLAMA_GENERATION_TIMEOUT", 120))


    # AnimeNewsNetwork API (no auth needed, just base URL)
    ANN_API_BASE_URL = "https://www.animenewsnetwork.com/encyclopedia/api.php"

    # One Piece API (no auth needed, just base URL)
    ONE_PIECE_API_BASE_URL = "https://api.api-onepiece.com/v2"

    # Aniwatch API Configuration (your locally hosted instance)
    ANIWATCH_API_BASE_URL = os.getenv("ANIWATCH_API_BASE_URL", "http://localhost:4444")


    # --- LLM Provider Selection ---
    # Dictionary of available LLM providers for the user to choose from for GENERATION
    # Now includes distinct entries for the two Ollama models
    LLM_PROVIDERS = {
        "gemini": "Google Gemini (Cloud)",
        "ollama_anime": "Ollama Anime Expert (Local)",
        "ollama_qwen": "Ollama Qwen2.5 (Local)"
    }
    # This variable will store the currently selected LLM for generation.
    # It can be updated via an API call from the frontend.
    # DEFAULT to the new anime Ollama model if DEFAULT_GENERATION_LLM is not set in .env
    CURRENT_GENERATION_LLM = os.getenv("DEFAULT_GENERATION_LLM", "ollama_anime")

    # Flask App Configuration
    # Set DEBUG to True directly to ensure it's always on for development.
    # This will show errors in the terminal and enable auto-reloading.
    DEBUG = True
    PORT = int(os.getenv("FLASK_PORT", 8001))
    HOST = os.getenv("FLASK_HOST", "127.0.0.1")

    # Vector Store Configuration
    # Path for the persistent vector store data, relative to the backend directory
    # This ensures the .pkl.gz file is created/loaded in the same directory as config.py
    VECTOR_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vector_db.pkl.gz')

    # --- Scheduler Configuration ---
    # Interval in minutes for how often the data embedding service should update
    EMBEDDING_UPDATE_INTERVAL_MINUTES = int(os.getenv("EMBEDDING_UPDATE_INTERVAL_MINUTES", 1440)) # Default to 24 hours

