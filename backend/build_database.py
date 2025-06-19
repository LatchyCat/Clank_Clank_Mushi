# backend/build_database.py
import logging
import os

# Set up logging before importing other modules
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

# Import global services. This needs to be after logging is configured.
from globals import (
    global_vector_store,
    global_data_embedding_service,
    global_clustering_service
)
from services.clustering_service import CLUSTER_CACHE_PATH

def build_database():
    """
    Performs a one-time, full data ingestion, embedding, and clustering pipeline.
    This script should be run manually whenever the source data changes or
    to create the database for the first time.
    """
    logging.info("--- Starting Database Build Process ---")

    # Step 1: Clear any existing data to ensure a fresh build.
    # This prevents partial updates and ensures consistency.
    logging.info("Clearing existing vector store and cache to ensure a fresh build...")
    global_vector_store.clear()
    if os.path.exists(CLUSTER_CACHE_PATH):
        try:
            os.remove(CLUSTER_CACHE_PATH)
            logging.info(f"Removed old cluster cache: {CLUSTER_CACHE_PATH}")
        except OSError as e:
            logging.error(f"Error removing cluster cache file: {e}")

    # Step 2: Ingest and embed all data from all sources.
    # This process populates the in-memory vector store and saves it.
    logging.info("Starting data ingestion and embedding...")
    global_data_embedding_service.embed_all_data()

    # Step 3: Pre-compute and cache all cluster variations.
    # This reads from the now-populated vector store.
    logging.info("Starting cluster pre-computation...")
    global_clustering_service.precompute_and_cache_all_clusters()

    logging.info("--- Database Build Process Completed Successfully! ---")
    logging.info(f"Vector store saved to: {global_vector_store.db_path} & {global_vector_store.index_path}")
    logging.info(f"Cluster cache saved to: {CLUSTER_CACHE_PATH}")
    logging.info("You can now start the Flask server with 'python3 app.py'")

if __name__ == "__main__":
    build_database()
