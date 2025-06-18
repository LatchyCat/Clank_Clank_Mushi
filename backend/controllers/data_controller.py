# backend/controllers/data_controller.py
import logging
from typing import Tuple, Dict, Any, Optional, List
from services.clustering_service import ClusteringService
from services.data_embedding_service import DataEmbeddingService
from globals import global_vector_store
import time

logger = logging.getLogger(__name__)

# --- START OF FIX: Implement Caching ---
# In-memory cache to store the results of expensive clustering operations.
# The key will be the number of clusters, and the value will be the response data.
cluster_cache = {}
CACHE_EXPIRATION_SECONDS = 3600  # Cache results for 1 hour (3600 seconds)
# --- END OF FIX ---


class DataController:
    _clustering_service: Optional[ClusteringService] = None
    _data_embedding_service: Optional[DataEmbeddingService] = None

    @classmethod
    def initialize(cls, clustering_service: ClusteringService, data_embedding_service: DataEmbeddingService):
        if cls._clustering_service is None:
            cls._clustering_service = clustering_service
            logger.info("DataController: Initialized with ClusteringService.")
        if cls._data_embedding_service is None:
            cls._data_embedding_service = data_embedding_service
            logger.info("DataController: Initialized with DataEmbeddingService.")

    @classmethod
    def get_clustered_documents(cls, num_clusters: int = 5) -> Tuple[Dict[str, Any], int]:
        if not cls._clustering_service:
            logger.error("DataController: ClusteringService not initialized.")
            return {"error": "Clustering service not available."}, 500

        # --- START OF FIX: Check cache before performing expensive operation ---
        cache_key = num_clusters
        cached_item = cluster_cache.get(cache_key)

        if cached_item and (time.time() - cached_item['timestamp'] < CACHE_EXPIRATION_SECONDS):
            logger.info(f"DataController: Returning cached result for {num_clusters} clusters.")
            return cached_item['data'], 200
        # --- END OF FIX ---

        logger.info(f"DataController: Cache miss or expired. Calculating new clusters for n={num_clusters}.")
        try:
            global_vector_store.load() # Ensure latest data is loaded from disk

            clustered_docs, cluster_info = cls._clustering_service.perform_kmeans_clustering(num_clusters)

            if not clustered_docs and not cluster_info:
                 logger.error("Clustering service returned no data.")
                 return {"error": "Clustering failed to produce results."}, 500

            response_data = {"documents": clustered_docs, "cluster_info": cluster_info}

            # --- START OF FIX: Store the new result in the cache ---
            cluster_cache[cache_key] = {
                'data': response_data,
                'timestamp': time.time()
            }
            # --- END OF FIX ---

            logger.info(f"DataController: Successfully retrieved and cached clustered data for n={num_clusters}.")
            return response_data, 200
        except Exception as e:
            logger.error(f"DataController: Error retrieving clustered documents: {e}", exc_info=True)
            return {"error": f"Failed to retrieve clustered documents: {str(e)}"}, 500

    @classmethod
    def ingest_anime_api_category_data(cls, categories: Optional[List[str]] = None, limit_per_category: int = 50) -> Tuple[Dict[str, Any], int]:
        if not cls._data_embedding_service:
            return {"error": "Data embedding service not available."}, 500
        try:
            processed, failed = cls._data_embedding_service.embed_anime_api_category_data(categories, limit_per_category)
            global_vector_store.save()
            cluster_cache.clear() # IMPORTANT: Clear cache after ingesting new data
            return {"message": f"Ingestion complete. Processed: {processed}, Failed: {failed}.", "processed": processed, "failed": failed}, 200
        except Exception as e:
            return {"error": f"Failed to ingest data: {str(e)}"}, 500

    @classmethod
    def ingest_all_data(cls) -> Tuple[Dict[str, Any], int]:
        if not cls._data_embedding_service:
            return {"error": "Data embedding service not available."}, 500
        try:
            cls._data_embedding_service.embed_all_data()
            cluster_cache.clear() # IMPORTANT: Clear cache after ingesting new data
            return {"message": f"All data sources ingested. Store has {len(global_vector_store.documents)} documents."}, 200
        except Exception as e:
            return {"error": f"Failed to ingest all data: {str(e)}"}, 500
