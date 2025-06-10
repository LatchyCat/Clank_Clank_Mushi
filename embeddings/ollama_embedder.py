# backend/embeddings/ollama_embedder.py
import requests
import json
from config import Config

class OllamaEmbedder:
    """
    Handles generating embeddings using a local Ollama instance.
    """
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.embedding_model = Config.OLLAMA_EMBEDDING_MODEL
        self.headers = {'Content-Type': 'application/json'}

    def embed_text(self, text: str) -> list[float] | None:
        """
        Generates an embedding for the given text using the configured Ollama model.

        Args:
            text (str): The text to embed.

        Returns:
            list[float] | None: A list of floats representing the embedding vector,
                                 or None if an error occurs.
        """
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.embedding_model,
            "prompt": text
        }
        print(f"DEBUG: OllamaEmbedder: Sending embedding request for text (first 50 chars): '{text[:50]}...'")
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=60)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            embedding_data = response.json()
            if 'embedding' in embedding_data:
                print("DEBUG: OllamaEmbedder: Successfully generated embedding.")
                return embedding_data['embedding']
            else:
                print(f"ERROR: OllamaEmbedder: 'embedding' key not found in response: {embedding_data}")
                return None
        except requests.exceptions.ConnectionError as e:
            print(f"ERROR: OllamaEmbedder: Connection error to Ollama server at {url}: {e}")
            return None
        except requests.exceptions.Timeout:
            print(f"ERROR: OllamaEmbedder: Embedding request timed out for model {self.embedding_model}.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"ERROR: OllamaEmbedder: An error occurred during embedding request: {e}")
            return None
        except json.JSONDecodeError:
            print(f"ERROR: OllamaEmbedder: Failed to decode JSON response from Ollama: {response.text if 'response' in locals() else 'No response'}")
            return None
        except Exception as e:
            print(f"ERROR: OllamaEmbedder: An unexpected error occurred: {e}")
            return None
