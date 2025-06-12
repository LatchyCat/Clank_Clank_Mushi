# backend/controllers/data_controller.py
import logging
from typing import Tuple, List, Dict, Any

# Import the ClusteringService
from services.clustering_service import ClusteringService

logger = logging.getLogger(__name__)

class DataController:
    """
    Manages data-related operations, including retrieving clustered document data.
    """
    # This class will hold the ClusteringService instance.
    # We will initialize it when the Flask app starts.
    _clustering_service: ClusteringService | None = None

    @classmethod
    def initialize(cls, clustering_service: ClusteringService):
        """Initializes the DataController with a ClusteringService instance."""
        if cls._clustering_service is None:
            cls._clustering_service = clustering_service
            logger.info("DataController: Initialized with ClusteringService.")
        else:
            logger.warning("DataController: Already initialized. Skipping re-initialization.")


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
            # The cluster_info can also be returned if the frontend needs it (e.g., centroids)
            # For now, we'll just return the docs with labels.
            return {"documents": clustered_docs, "cluster_info": cluster_info}, 200
        except Exception as e:
            logger.error(f"DataController: Error retrieving clustered documents: {e}")
            return {"error": "Failed to retrieve clustered data.", "details": str(e)}, 500
