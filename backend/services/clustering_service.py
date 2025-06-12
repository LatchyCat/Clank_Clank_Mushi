# backend/services/clustering_service.py
import numpy as np
from sklearn.cluster import KMeans
from typing import List, Dict, Any, Tuple
import logging

# Import the VectorStore from its location
from embeddings.vector_store import VectorStore

logger = logging.getLogger(__name__)

class ClusteringService:
    """
    Handles the clustering of document embeddings using K-Means.
    """
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        logger.info("ClusteringService: Initialized.")

    def perform_kmeans_clustering(self, n_clusters: int = 5) -> Tuple[List[Dict[str, Any]], Dict[int, Any]]:
        """
        Performs K-Means clustering on all documents in the vector store.

        Args:
            n_clusters (int): The number of clusters to form.

        Returns:
            Tuple[List[Dict[str, Any]], Dict[int, Any]]:
                - A list of documents, each augmented with a 'cluster_label' field.
                - A dictionary containing information about each cluster (e.g., centroid).
        """
        all_documents = self.vector_store.get_all_documents_with_embeddings()

        if not all_documents:
            logger.warning("ClusteringService: No documents found in vector store to cluster.")
            return [], {}

        # Extract embeddings as a 2D NumPy array
        # Ensure all embeddings are actually NumPy arrays. If not, convert them.
        embeddings = []
        for doc in all_documents:
            embedding = doc.get("embedding")
            if isinstance(embedding, np.ndarray):
                embeddings.append(embedding)
            elif isinstance(embedding, list):
                embeddings.append(np.array(embedding))
            else:
                logger.warning(f"ClusteringService: Document ID {doc.get('id', 'N/A')} has invalid embedding type: {type(embedding)}. Skipping.")

        if not embeddings:
            logger.warning("ClusteringService: No valid embeddings found to cluster.")
            return [], {}

        embeddings_array = np.array(embeddings)

        # Ensure n_clusters is not greater than the number of samples
        if n_clusters > len(embeddings_array):
            logger.warning(f"ClusteringService: n_clusters ({n_clusters}) is greater than the number of documents ({len(embeddings_array)}). Setting n_clusters to number of documents.")
            n_clusters = len(embeddings_array)
            if n_clusters == 0:
                return [], {} # No documents to cluster

        try:
            # Initialize KMeans. Using n_init='auto' (default in recent sklearn) or a specific number.
            # random_state for reproducibility.
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            cluster_labels = kmeans.fit_predict(embeddings_array)

            clustered_documents = []
            for i, doc in enumerate(all_documents):
                doc_copy = doc.copy()
                doc_copy['cluster_label'] = int(cluster_labels[i]) # Ensure label is standard int
                # Convert embedding back to a list for JSON serialization in API response
                if isinstance(doc_copy.get('embedding'), np.ndarray):
                    doc_copy['embedding'] = doc_copy['embedding'].tolist()
                clustered_documents.append(doc_copy)

            # Prepare cluster insights (e.g., centroids, sizes)
            cluster_info = {}
            for i, centroid in enumerate(kmeans.cluster_centers_):
                cluster_info[i] = {
                    "centroid": centroid.tolist(), # Convert centroid to list for JSON serialization
                    "document_count": sum(1 for label in cluster_labels if label == i)
                }

            logger.info(f"ClusteringService: Successfully clustered {len(all_documents)} documents into {n_clusters} clusters.")
            return clustered_documents, cluster_info

        except ValueError as e:
            logger.error(f"ClusteringService: ValueError during K-Means clustering: {e}")
            return [], {}
        except Exception as e:
            logger.error(f"ClusteringService: An unexpected error occurred during clustering: {e}")
            return [], {}
