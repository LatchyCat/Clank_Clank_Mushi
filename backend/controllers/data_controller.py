# backend/controllers/data_controller.py
import logging
from typing import Tuple, Dict, Any, List, Optional
import json
import os
from services.clustering_service import ClusteringService, CLUSTER_CACHE_PATH
from services.data_embedding_service import DataEmbeddingService

logger = logging.getLogger(__name__)

class DataController:
    _clustering_service: Optional[ClusteringService] = None
    _data_embedding_service: Optional[DataEmbeddingService] = None

    @classmethod
    def initialize(cls, clustering_service: ClusteringService, data_embedding_service: DataEmbeddingService):
        cls._clustering_service = clustering_service
        cls._data_embedding_service = data_embedding_service
        logger.debug("DataController: Services initialized.")

    @classmethod
    def get_clustered_documents(cls, num_clusters: int = 5) -> Tuple[Dict[str, Any], int]:
        logger.info(f"API Request: /api/data/clusters with n_clusters={num_clusters}")
        try:
            if not os.path.exists(CLUSTER_CACHE_PATH):
                logger.warning("Cluster cache file not found. Database may still be populating.")
                return {"error": "Cluster data not available yet. Please wait for background processing to complete."}, 404

            with open(CLUSTER_CACHE_PATH, 'r') as f:
                full_cache = json.load(f)

            cluster_data = full_cache.get(str(num_clusters))

            if not cluster_data:
                logger.error(f"No cached data found for n_clusters={num_clusters}")
                return {"error": f"No pre-computed data available for {num_clusters} clusters. Please trigger a re-ingestion if needed."}, 404

            return cluster_data, 200

        except FileNotFoundError:
             return {"error": "Cluster cache not found. The background processing job may not have run yet."}, 404
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from cluster cache file: {CLUSTER_CACHE_PATH}", exc_info=True)
            return {"error": "Failed to read cluster data from a corrupted cache. A re-ingestion may be required."}, 500
        except Exception as e:
            logger.error(f"Error reading cluster cache file: {e}", exc_info=True)
            return {"error": "Failed to read cluster data from cache."}, 500

    @classmethod
    def ingest_all_data(cls) -> Tuple[Dict[str, Any], int]:
        if not cls._data_embedding_service or not cls._clustering_service:
            logger.error("DataController: A required service is not initialized.")
            return {"error": "A required service is not available."}, 500
        try:
            logger.info("Triggering full data ingestion and cluster pre-computation via API...")
            cls._data_embedding_service.embed_all_data()
            cls._clustering_service.precompute_and_cache_all_clusters()
            return {"message": "Full data ingestion and cluster pre-computation complete."}, 200
        except Exception as e:
            logger.error(f"Error during full data ingestion: {e}", exc_info=True)
            return {"error": f"Failed to ingest all data: {str(e)}"}, 500

    @classmethod
    def ingest_anime_api_category_data(cls, categories: List[str], limit_per_category: int) -> Tuple[Dict[str, Any], int]:
        if not cls._data_embedding_service or not cls._clustering_service:
            logger.error("DataController: A required service is not initialized.")
            return {"error": "A required service is not available."}, 500
        try:
            logger.info(f"Triggering category data ingestion for {categories} and re-computing clusters via API...")
            cls._data_embedding_service.embed_anime_api_by_category(categories, limit_per_category)
            cls._clustering_service.precompute_and_cache_all_clusters()
            return {"message": "Category data ingested and clusters re-computed."}, 200
        except Exception as e:
            logger.error(f"Error during category ingestion controller logic: {e}", exc_info=True)
            return {"error": f"Failed to ingest category data: {str(e)}"}, 500
