# backend/embeddings/ollama_embedder.py
import requests
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class OllamaEmbedder:
    """
    Handles generating embeddings using a local Ollama instance.
    """
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.embedding_model = Config.OLLAMA_EMBEDDING_MODEL
        self.headers = {'Content-Type': 'application/json'}
        if not self._verify_model_exists():
            error_msg = (
                f"FATAL: The specified embedding model '{self.embedding_model}' does not exist in your local Ollama instance. "
                f"Please run 'ollama pull {self.embedding_model}' in your terminal to download it."
            )
            logger.critical(error_msg)
            raise ValueError(error_msg)

    def _verify_model_exists(self) -> bool:
        """Checks if the configured embedding model is available in the Ollama instance."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            for model in models:
                if model.get("name").startswith(self.embedding_model):
                    logger.info(f"OllamaEmbedder: Verified that model '{self.embedding_model}' is available.")
                    return True
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"OllamaEmbedder: Could not connect to Ollama at {self.base_url} to verify model existence. Error: {e}")
            return False

    def embed_text(self, text: str) -> list[float] | None:
        """
        Generates an embedding for the given text using the configured Ollama model.
        """
        # --- START OF DEFINITIVE FIX: Use correct endpoint AND payload key ---
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.embedding_model,
            "prompt": text  # The correct key for the embedding text is 'prompt'.
        }
        # --- END OF DEFINITIVE FIX ---

        logger.debug(f"OllamaEmbedder: Sending embedding request for text (first 50 chars): '{text[:50]}...'")
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()
            embedding_data = response.json()

            # The /api/embeddings endpoint returns 'embedding'.
            if 'embedding' in embedding_data:
                logger.debug("OllamaEmbedder: Successfully generated embedding.")
                return embedding_data['embedding']
            else:
                logger.error(f"OllamaEmbedder: 'embedding' key not found in response: {embedding_data}")
                return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"OllamaEmbedder: Connection error to Ollama server at {url}: {e}")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"OllamaEmbedder: Embedding request timed out for model {self.embedding_model}.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"OllamaEmbedder: An error occurred during embedding request: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"OllamaEmbedder: Failed to decode JSON response from Ollama: {response.text if 'response' in locals() else 'No response'}")
            return None
        except Exception as e:
            logger.error(f"OllamaEmbedder: An unexpected error occurred: {e}")
            return None
