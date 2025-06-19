# backend/services/clustering_service.py
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
import logging
from collections import Counter
import re
import json
import os
from config import Config
from services.ollama_llm_service import OllamaLLMService

logger = logging.getLogger(__name__)

# Define a path for the pre-computed cluster cache file
CLUSTER_CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cluster_cache.json')

class ClusteringService:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm_service = OllamaLLMService(model_name=Config.OLLAMA_DEFAULT_GENERATION_MODEL)
        logger.info("ClusteringService: Initialized with LLM for titling.")

    def precompute_and_cache_all_clusters(self, min_clusters=2, max_clusters=10):
        """
        Performs clustering for a range of cluster numbers and saves the results to a file.
        This is an expensive operation meant to be run in the background.
        """
        logger.info(f"Starting pre-computation of clusters from {min_clusters} to {max_clusters}...")
        all_documents = self.vector_store.get_all_documents_with_embeddings()
        if not all_documents:
            logger.warning("No documents with embeddings found. Skipping cluster pre-computation.")
            return

        embeddings = [doc["embedding"] for doc in all_documents if "embedding" in doc]
        if not embeddings:
            logger.warning("No embeddings found in the documents. Skipping cluster pre-computation.")
            return

        embeddings_array = np.array(embeddings, dtype='float32')
        full_cache = {}

        for n_clusters in range(min_clusters, max_clusters + 1):
            if n_clusters > len(embeddings):
                logger.warning(f"Skipping n_clusters={n_clusters} as it's more than the number of documents.")
                continue

            logger.info(f"--- Computing for n_clusters = {n_clusters} ---")
            try:
                doc_id_to_label, cluster_info = self._perform_single_kmeans_run(embeddings_array, all_documents, n_clusters)
                if doc_id_to_label and cluster_info:
                    full_cache[str(n_clusters)] = {
                        "doc_id_to_label": doc_id_to_label,
                        "cluster_info": cluster_info
                    }
                else:
                    logger.error(f"Failed to generate valid data for n_clusters = {n_clusters}")
            except Exception as e:
                logger.error(f"Error processing n_clusters={n_clusters}: {e}", exc_info=True)

        try:
            with open(CLUSTER_CACHE_PATH, 'w') as f:
                json.dump(full_cache, f, indent=2)
            logger.info(f"Successfully pre-computed and cached all cluster variations to {CLUSTER_CACHE_PATH}")
        except Exception as e:
            logger.error(f"Failed to write cluster cache to file: {e}")

    def _perform_single_kmeans_run(self, embeddings_array: np.ndarray, all_documents: List[Dict], n_clusters: int) -> Tuple[Dict[str, Any], Dict[int, Any]]:
        """Performs a single K-Means run for a given number of clusters."""
        dimension = embeddings_array.shape[1]
        kmeans = faiss.Kmeans(dimension, n_clusters, niter=20, verbose=False)
        kmeans.train(embeddings_array)
        _, labels = kmeans.index.search(embeddings_array, 1)

        doc_id_to_label = {
            doc["source_item_id"]: int(labels[i][0])
            for i, doc in enumerate(all_documents) if "embedding" in doc and "source_item_id" in doc
        }

        clustered_docs_by_label = [[] for _ in range(n_clusters)]
        for i, doc in enumerate(all_documents):
            if "embedding" in doc:
                label = int(labels.ravel()[i])
                clustered_docs_by_label[label].append(doc)

        all_cluster_keywords = self._get_top_terms_for_all_clusters(clustered_docs_by_label)
        all_cluster_titles = self._get_llm_cluster_titles_iteratively(all_cluster_keywords)

        cluster_info = {}
        for i in range(n_clusters):
            cluster_info[i] = {
                "title": all_cluster_titles.get(i, f"Cluster {i}"),
                "top_terms": all_cluster_keywords.get(i, []),
            }

        return doc_id_to_label, cluster_info

    def _get_top_terms_for_all_clusters(self, clustered_docs_by_label: List[List[Dict]], top_n: int = 5) -> Dict[int, List[str]]:
        stop_words = set(['a', 'an', 'and', 'the', 'is', 'it', 'in', 'on', 'of', 'for', 'with', 'to', 'n', 'd','s', 'as', 'by', 'title', 'synopsis', 'description', 'genres', 'type', 'anime', 'user', 'its','manga', 'movie', 'character', 'episode', 'series', 'story', 'one', 'two', 'can', 'airing', 'no','he', 'she', 'they', 'his', 'her', 'their', 'has', 'have', 'was', 'were', 'from', 'can','that', 'this', 'but', 'are', 'not', 'be', 'at', 'who', 'all', 'into', 'about', 'after'])
        cluster_keywords = {}
        for i, docs in enumerate(clustered_docs_by_label):
            all_words = []
            for doc in docs:
                content = doc.get('content', '')
                words = re.findall(r'\b\w{3,}\b', content.lower())
                all_words.extend([word for word in words if word not in stop_words and not word.isdigit()])
            if all_words:
                cluster_keywords[i] = [word for word, count in Counter(all_words).most_common(top_n)]
            else:
                cluster_keywords[i] = []
        return cluster_keywords

    def _get_llm_cluster_titles_iteratively(self, all_keywords: Dict[int, List[str]]) -> Dict[int, str]:
        """
        Generates cluster titles by making a separate, simpler LLM call for each cluster.
        This is more robust against timeouts and complex parsing errors.
        """
        if not all_keywords:
            return {}

        all_titles = {}
        for cluster_id, keywords in all_keywords.items():
            if not keywords:
                all_titles[cluster_id] = f"Cluster {cluster_id}"
                continue

            prompt = (
                "You are an expert at creating concise, descriptive titles. "
                f"Based on these keywords: {', '.join(keywords)}, "
                "generate a single, short title for this topic cluster. "
                "**Respond with ONLY the title itself, and nothing else. Do not use any XML or markdown tags.**"
            )

            try:
                logger.info(f"Requesting title for Cluster {cluster_id} with keywords: {keywords}")
                response_str = self.llm_service.get_simple_response(prompt)

                if response_str and not response_str.startswith("Error:"):
                    # --- START OF FIX: Robust Tag and Artifact Stripping ---
                    # 1. Remove any <think>...</think> blocks first.
                    cleaned_str = re.sub(r'<think>.*?</think>', '', response_str, flags=re.DOTALL)
                    # 2. Remove any other XML-like tags (e.g., <mood>, <spoiler>).
                    cleaned_str = re.sub(r'<[^>]+>', '', cleaned_str)
                    # 3. Strip leading/trailing whitespace and quotes.
                    title = cleaned_str.strip().strip("'\"")
                    # --- END OF FIX ---

                    all_titles[cluster_id] = title
                    logger.info(f"Successfully generated title for Cluster {cluster_id}: '{title}'")
                else:
                    raise Exception(f"LLM returned an error or empty response: {response_str}")

            except Exception as e:
                logger.warning(f"LLM titling failed for Cluster {cluster_id}: {e}. Using fallback.")
                # Fallback for a single cluster if it fails
                all_titles[cluster_id] = ", ".join(keywords[:3]).capitalize()

        return all_titles
