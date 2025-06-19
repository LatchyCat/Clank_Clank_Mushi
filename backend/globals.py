# backend/globals.py
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.vector_store import VectorStore
from services.clustering_service import ClusteringService
from services.data_embedding_service import DataEmbeddingService
from services.anime_api_service import AnimeAPIService
from controllers.anime_controller import AnimeController
from config import Config

# Initialize services and controllers in the correct order

# 1. Core services that don't depend on others
global_vector_store = VectorStore(db_path=Config.VECTOR_DB_PATH)
global_ollama_embedder = OllamaEmbedder()
global_anime_api_service = AnimeAPIService() # This is used by the controller

# 2. Controllers that depend on core services
# The AnimeController now correctly gets the anime_api_service it needs.
global_anime_controller = AnimeController(anime_api_service=global_anime_api_service)

# 3. High-level services that depend on other services and controllers
global_clustering_service = ClusteringService(vector_store=global_vector_store)
global_data_embedding_service = DataEmbeddingService(
    vector_store=global_vector_store,
    embedder=global_ollama_embedder,
    anime_controller=global_anime_controller # Pass the correctly instantiated controller
)

print("DEBUG: globals.py: All global services and controllers initialized correctly.")
