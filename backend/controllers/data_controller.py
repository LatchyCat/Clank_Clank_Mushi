# backend/controllers/data_controller.py
import logging
from typing import Tuple, List, Dict, Any, Optional
from services.clustering_service import ClusteringService
from services.data_embedding_service import DataEmbeddingService
from globals import global_vector_store

logger = logging.getLogger(__name__)

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

        logger.info(f"DataController: Retrieving clustered documents with {num_clusters} clusters...")
        try:
            global_vector_store.load()
            # Note: The service method was renamed in the thought process, let's keep it consistent.
            # Assuming it's `perform_kmeans_clustering` which returns a tuple.
            clustered_docs, cluster_info = cls._clustering_service.perform_kmeans_clustering(num_clusters)
            response_data = {"documents": clustered_docs, "cluster_info": cluster_info}
            logger.info(f"DataController: Successfully retrieved clustered data.")
            return response_data, 200
        except Exception as e:
            logger.error(f"DataController: Error retrieving clustered documents: {e}", exc_info=True)
            return {"error": f"Failed to retrieve clustered documents: {str(e)}"}, 500

    @classmethod
    def ingest_anime_api_category_data(cls, categories: Optional[List[str]] = None, limit_per_category: int = 50) -> Tuple[Dict[str, Any], int]:
        if not cls._data_embedding_service:
            logger.error("DataController: DataEmbeddingService not initialized.")
            return {"error": "Data embedding service not available."}, 500

        logger.info(f"DataController: Starting Anime API category data ingestion for: {categories}...")
        try:
            processed, failed = cls._data_embedding_service.embed_anime_api_category_data(
                categories=categories, limit_per_category=limit_per_category
            )
            global_vector_store.save()
            message = f"Anime API category data ingestion complete. Processed: {processed}, Failed: {failed}."
            logger.info(message)
            return {"message": message, "processed": processed, "failed": failed}, 200
        except Exception as e:
            logger.error(f"DataController: Error during Anime API category data ingestion: {e}", exc_info=True)
            return {"error": f"Failed to ingest Anime API category data: {str(e)}"}, 500

    @classmethod
    def ingest_all_data(cls) -> Tuple[Dict[str, Any], int]:
        if not cls._data_embedding_service:
            logger.error("DataController: DataEmbeddingService not initialized.")
            return {"error": "Data embedding service not available."}, 500

        logger.info("DataController: Starting ingestion of all data sources...")
        try:
            cls._data_embedding_service.embed_all_data()
            message = f"All data sources ingestion complete. Vector store now contains {len(global_vector_store.documents)} documents."
            logger.info(message)
            return {"message": message}, 200
        except Exception as e:
            logger.error(f"DataController: Error during all data ingestion: {e}", exc_info=True)
            return {"error": f"Failed to ingest all data: {str(e)}"}, 500
