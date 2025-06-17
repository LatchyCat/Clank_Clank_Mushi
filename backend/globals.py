# backend/globals.py
from embeddings.ollama_embedder import OllamaEmbedder
from embeddings.vector_store import VectorStore
from services.clustering_service import ClusteringService
from services.data_embedding_service import DataEmbeddingService
from services.anime_api_service import AnimeAPIService
from controllers.anime_controller import AnimeController # Import controller
from config import Config

global_vector_store = VectorStore(db_path=Config.VECTOR_DB_PATH)
global_ollama_embedder = OllamaEmbedder()
global_clustering_service = ClusteringService(vector_store=global_vector_store)
global_anime_api_service = AnimeAPIService()
# Create an instance of the controller to pass to the embedding service
global_anime_controller = AnimeController()

# Pass the controller to the embedding service
global_data_embedding_service = DataEmbeddingService(
    vector_store=global_vector_store,
    embedder=global_ollama_embedder,
    anime_controller=global_anime_controller # Pass the controller instance
)

print("DEBUG: globals.py: Initialized global services and controllers.")
