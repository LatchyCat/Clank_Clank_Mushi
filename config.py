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
    OLLAMA_GENERATION_MODEL = "qwen2.5:3b"       # User-selectable Ollama model

    # AnimeNewsNetwork API (no auth needed, just base URL)
    ANN_API_BASE_URL = "https://www.animenewsnetwork.com/encyclopedia/api.php"

    # One Piece API (no auth needed, just base URL)
    ONE_PIECE_API_BASE_URL = "https://api.api-onepiece.com/v2"

    # --- LLM Provider Selection ---
    # Dictionary of available LLM providers for the user to choose from for GENERATION
    LLM_PROVIDERS = {
        "gemini": "Google Gemini (Cloud)",
        "ollama": "Ollama Qwen2.5 (Local)" # Key "ollama" is correct for controller
    }
    # This variable will store the currently selected LLM for generation.
    # It can be updated via an API call from the frontend.
    # DEFAULT to Ollama if DEFAULT_GENERATION_LLM is not set in .env
    CURRENT_GENERATION_LLM = os.getenv("DEFAULT_GENERATION_LLM", "ollama")

    # Flask App Configuration
    # Set DEBUG to True directly to ensure it's always on for development.
    # This will show errors in the terminal and enable auto-reloading.
    DEBUG = True
    PORT = int(os.getenv("FLASK_PORT", 8001))
    HOST = os.getenv("FLASK_HOST", "127.0.0.1") 
