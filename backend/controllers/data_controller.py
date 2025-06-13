# backend/controllers/data_controller.py
import logging
from typing import Tuple, List, Dict, Any

# Import the ClusteringService
from services.clustering_service import ClusteringService
# Import the DataEmbeddingService and global_vector_store
from services.data_embedding_service import DataEmbeddingService
from globals import global_vector_store # Needed to save the vector store

logger = logging.getLogger(__name__)

class DataController:
    """
    Manages data-related operations, including retrieving clustered document data
    and triggering data ingestion processes.
    """
    # This class will hold the ClusteringService and DataEmbeddingService instances.
    _clustering_service: ClusteringService | None = None
    _data_embedding_service: DataEmbeddingService | None = None # Add data embedding service

    @classmethod
    def initialize(cls, clustering_service: ClusteringService, data_embedding_service: DataEmbeddingService):
        """Initializes the DataController with service instances."""
        if cls._clustering_service is None:
            cls._clustering_service = clustering_service
            logger.info("DataController: Initialized with ClusteringService.")
        else:
            logger.warning("DataController: ClusteringService already initialized.")

        if cls._data_embedding_service is None:
            cls._data_embedding_service = data_embedding_service
            logger.info("DataController: Initialized with DataEmbeddingService.")
        else:
            logger.warning("DataController: DataEmbeddingService already initialized.")


    @classmethod
    def get_clustered_documents(cls, num_clusters: int = 5) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieves all documents from the vector store, performs clustering,
        and returns the documents with their cluster labels.

        Args:
            num_clusters (int): The desired number of clusters for K-Means.

        Returns:
            Tuple[List[Dict[str, Any]], int]:
                - A list of documents, each with a 'cluster_label' field.
                - HTTP status code (200 for success, 500 for error).
        """
        if cls._clustering_service is None:
            logger.error("DataController: ClusteringService not initialized.")
            return {"error": "Clustering service not available."}, 500

        try:
            clustered_docs, cluster_info = cls._clustering_service.perform_kmeans_clustering(n_clusters=num_clusters)
            return {"documents": clustered_docs, "cluster_info": cluster_info}, 200
        except Exception as e:
            logger.error(f"DataController: Error retrieving clustered documents: {e}")
            return {"error": "Failed to retrieve clustered data.", "details": str(e)}, 500

    @classmethod
    def ingest_ann_data(cls, limit: int = 100) -> Tuple[Dict[str, Any], int]:
        """
        Triggers the ingestion and embedding of recent ANN data into the vector store.
        Args:
            limit (int): The maximum number of recent ANN items to fetch and process.
        Returns:
            Tuple[Dict[str, Any], int]: A message indicating success/failure and status code.
        """
        if cls._data_embedding_service is None:
            logger.error("DataController: DataEmbeddingService not initialized.")
            return {"error": "Data embedding service not available. Cannot ingest ANN data."}, 500

        logger.info(f"DataController: Starting ANN data ingestion with limit={limit}...")
        try:
            processed_count, failed_count = cls._data_embedding_service.embed_ann_details_data(limit=limit)
            global_vector_store.save() # Save the vector store after ingestion
            message = f"ANN data ingestion complete. Processed {processed_count} items. Failed: {failed_count}."
            logger.info(message)
            return {"message": message, "processed_count": processed_count, "failed_count": failed_count}, 200
        except Exception as e:
            logger.error(f"DataController: Error during ANN data ingestion: {e}")
            return {"error": f"Failed to ingest ANN data: {str(e)}"}, 500

    @classmethod
    def ingest_aniwatch_data(cls, limit: int = 100, page_limit: int = 5) -> Tuple[Dict[str, Any], int]:
        """
        Triggers the ingestion and embedding of Aniwatch anime data into the vector store.
        Args:
            limit (int): The maximum number of Aniwatch anime items to fetch and process.
            page_limit (int): The maximum number of A-Z list pages to fetch from Aniwatch API.
        Returns:
            Tuple[Dict[str, Any], int]: A message indicating success/failure and status code.
        """
        if cls._data_embedding_service is None:
            logger.error("DataController: DataEmbeddingService not initialized.")
            return {"error": "Data embedding service not available. Cannot ingest Aniwatch data."}, 500

        logger.info(f"DataController: Starting Aniwatch data ingestion with limit={limit}, page_limit={page_limit}...")
        try:
            processed_count, failed_count = cls._data_embedding_service.embed_aniwatch_data(limit=limit, page_limit=page_limit)
            global_vector_store.save() # Save the vector store after ingestion
            message = f"Aniwatch data ingestion complete. Processed {processed_count} items. Failed: {failed_count}."
            logger.info(message)
            return {"message": message, "processed_count": processed_count, "failed_count": failed_count}, 200
        except Exception as e:
            logger.error(f"DataController: Error during Aniwatch data ingestion: {e}")
            return {"error": f"Failed to ingest Aniwatch data: {str(e)}"}, 500
