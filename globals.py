# backend/globals.py
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.vector_store import VectorStore

# Initialize global instances for embedding components
# These will be initialized once when the application starts
global_vector_store = VectorStore()
global_ollama_embedder = OllamaEmbedder()

print("DEBUG: globals.py: Initialized global_vector_store and global_ollama_embedder.")
