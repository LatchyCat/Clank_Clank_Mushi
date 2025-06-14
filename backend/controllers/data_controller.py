# backend/controllers/data_controller.py
import logging
from typing import Tuple, List, Dict, Any, Optional # Added Optional

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
    _data_embedding_service: DataEmbeddingService | None = None

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
    def get_clustered_documents(cls, num_clusters: int = 5) -> Tuple[Dict[str, Any], int]:
        """
        Retrieves documents from the vector store and applies clustering.
        Args:
            num_clusters (int): The desired number of clusters.
        Returns:
            Tuple[Dict[str, Any], int]: A dictionary of clustered documents and HTTP status code.
        """
        if cls._clustering_service is None:
            logger.error("DataController: ClusteringService not initialized.")
            return {"error": "Clustering service not available."}, 500

        logger.info(f"DataController: Retrieving clustered documents with {num_clusters} clusters...")
        try:
            # Ensure the vector store is loaded before attempting to cluster
            global_vector_store.load()
            clustered_data = cls._clustering_service.get_clustered_documents(num_clusters)
            logger.info(f"DataController: Successfully retrieved clustered data with {len(clustered_data['clusters'])} clusters.")
            return clustered_data, 200
        except Exception as e:
            logger.error(f"DataController: Error retrieving clustered documents: {e}")
            return {"error": f"Failed to retrieve clustered documents: {str(e)}"}, 500

    @classmethod
    def ingest_ann_data(cls, limit: int = 100) -> Tuple[Dict[str, Any], int]:
        """
        Triggers the ingestion and embedding of recent ANN data into the vector store.
        Args:
            limit (int): The maximum number of ANN items to fetch and process.
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

    @classmethod
    def ingest_anime_api_data(cls, limit: int = 100) -> Tuple[Dict[str, Any], int]:
        """
        Triggers the ingestion and embedding of data from the new 'anime-api' Node.js project.
        Args:
            limit (int): The maximum number of anime items to fetch and process.
        Returns:
            Tuple[Dict[str, Any], int]: A message indicating success/failure and status code.
        """
        if cls._data_embedding_service is None:
            logger.error("DataController: DataEmbeddingService not initialized.")
            return {"error": "Data embedding service not available. Cannot ingest Anime API data."}, 500

        logger.info(f"DataController: Starting Anime API data ingestion with limit={limit}...")
        try:
            processed_count, failed_count = cls._data_embedding_service.embed_anime_api_data(limit=limit)
            global_vector_store.save()
            message = f"Anime API data ingestion complete. Processed {processed_count} items. Failed: {failed_count}."
            logger.info(message)
            return {"message": message, "processed_count": processed_count, "failed_count": failed_count}, 200
        except Exception as e:
            logger.error(f"DataController: Error during Anime API data ingestion: {e}")
            return {"error": f"Failed to ingest Anime API data: {str(e)}"}, 500

    @classmethod
    def ingest_anime_api_category_data(cls, categories: Optional[List[str]] = None, limit_per_category: int = 50) -> Tuple[Dict[str, Any], int]:
        """
        Triggers the ingestion of data from specific categories of the 'anime-api' Node.js project.
        Args:
            categories (List[str]): A list of categories to ingest. If None, default categories will be used.
            limit_per_category (int): The maximum number of anime titles to fetch and process per category.
        Returns:
            Tuple[Dict[str, Any], int]: A message indicating success/failure and status code.
        """
        if cls._data_embedding_service is None:
            logger.error("DataController: DataEmbeddingService not initialized.")
            return {"error": "Data embedding service not available. Cannot ingest AnimeAPI category data."}, 500

        logger.info(f"DataController: Starting Anime API category data ingestion for categories: {categories}, limit_per_category={limit_per_category}...")
        try:
            processed_count, failed_count = cls._data_embedding_service.embed_anime_api_category_data(
                categories=categories, limit_per_category=limit_per_category
            )
            global_vector_store.save()
            message = f"Anime API category data ingestion complete. Processed {processed_count} items. Failed: {failed_count}."
            logger.info(message)
            return {"message": message, "processed_count": processed_count, "failed_count": failed_count}, 200
        except Exception as e:
            logger.error(f"DataController: Error during Anime API category data ingestion: {e}")
            return {"error": f"Failed to ingest Anime API category data: {str(e)}"}, 500

    @classmethod
    def ingest_all_data(cls) -> Tuple[Dict[str, Any], int]:
        """
        Triggers the ingestion and embedding of data from ALL configured sources
        into the vector store. This includes One Piece, ANN, Aniwatch, and Anime API data.
        It performs de-duplication automatically.
        """
        if cls._data_embedding_service is None:
            logger.error("DataController: DataEmbeddingService not initialized.")
            return {"error": "Data embedding service not available. Cannot ingest all data."}, 500

        logger.info("DataController: Starting ingestion of all data sources...")
        try:
            cls._data_embedding_service.embed_all_data() # This method handles saving internally
            message = "All data sources ingestion complete. Vector store updated."
            logger.info(message)
            return {"message": message}, 200
        except Exception as e:
            logger.error(f"DataController: Error during all data ingestion: {e}")
            return {"error": f"Failed to ingest all data: {str(e)}"}, 500
