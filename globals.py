# backend/globals.py
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.vector_store import VectorStore
from config import Config # Import Config to get the DB path

# Initialize global instances for embedding components
# These will be initialized once when the application starts
# Pass the persistence path to the VectorStore
global_vector_store = VectorStore(db_path=Config.VECTOR_DB_PATH)
global_ollama_embedder = OllamaEmbedder()

print("DEBUG: globals.py: Initialized global_vector_store and global_ollama_embedder.")
