# backend/globals.py
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.vector_store import VectorStore
from services.clustering_service import ClusteringService # Import the new ClusteringService
from services.data_embedding_service import DataEmbeddingService # Import DataEmbeddingService
from services.anime_api_service import AnimeAPIService # NEW: Import AnimeAPIService
from config import Config # Import Config to get the DB path

# Initialize global instances for embedding components
# These will be initialized once when the application starts
# Pass the persistence path to the VectorStore
global_vector_store = VectorStore(db_path=Config.VECTOR_DB_PATH)
global_ollama_embedder = OllamaEmbedder()
# Initialize the global clustering service, passing the global vector store to it
global_clustering_service = ClusteringService(vector_store=global_vector_store)
# NEW: Initialize the global AnimeAPIService
global_anime_api_service = AnimeAPIService()
# Initialize the global data embedding service, passing the new anime_api_service to it
global_data_embedding_service = DataEmbeddingService(
    vector_store=global_vector_store,
    embedder=global_ollama_embedder,
    anime_api_service=global_anime_api_service # Pass the new service here
)

print("DEBUG: globals.py: Initialized global_vector_store, global_ollama_embedder, global_clustering_service, global_anime_api_service, and global_data_embedding_service.")
