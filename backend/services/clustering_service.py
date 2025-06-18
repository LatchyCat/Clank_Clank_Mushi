# backend/services/clustering_service.py
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from typing import List, Dict, Any, Tuple
import logging
from collections import Counter
import re
import json

# We still need the LLM service to generate titles
from services.ollama_llm_service import OllamaLLMService
from config import Config

logger = logging.getLogger(__name__)

class ClusteringService:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        # Initialize the service once for the class instance
        self.llm_service = OllamaLLMService(model_name=Config.OLLAMA_DEFAULT_GENERATION_MODEL)
        logger.info("ClusteringService: Initialized with LLM for titling.")

    def _get_top_terms_for_all_clusters(self, clustered_docs_by_label: List[List[Dict]], top_n: int = 5) -> Dict[int, List[str]]:
        """Calculates top terms for all clusters efficiently."""
        stop_words = set([
            'a', 'an', 'and', 'the', 'is', 'it', 'in', 'on', 'of', 'for', 'with', 'to', 'n', 'd',
            's', 'as', 'by', 'title', 'synopsis', 'description', 'genres', 'type', 'anime', 'user', 'its',
            'manga', 'movie', 'character', 'episode', 'series', 'story', 'one', 'two', 'can', 'airing', 'no',
            'he', 'she', 'they', 'his', 'her', 'their', 'has', 'have', 'was', 'were', 'from', 'can',
            'that', 'this', 'but', 'are', 'not', 'be', 'at', 'who', 'all', 'into', 'about', 'after'
        ])

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

    def _get_llm_cluster_titles_in_batch(self, all_keywords: Dict[int, List[str]]) -> Dict[int, str]:
        """
        --- OPTIMIZATION: SINGLE BATCH LLM CALL ---
        Generates titles for all clusters in a single request to the LLM.
        """
        if not all_keywords: return {}

        # Prepare the input for the LLM in a structured format
        prompt_input = ""
        for cluster_id, keywords in all_keywords.items():
            if keywords:
                prompt_input += f"Cluster {cluster_id} Keywords: {', '.join(keywords)}\n"

        if not prompt_input: return {}

        prompt = (
            "You are an expert at summarizing topics. Below are keyword sets for several clusters of anime-related documents. "
            "For each cluster, generate a short, concise, and compelling title (4-5 words max). "
            "Respond with ONLY a single, valid JSON object where keys are the cluster IDs (as strings) and values are the generated titles.\n\n"
            "EXAMPLE INPUT:\n"
            "Cluster 0 Keywords: luffy, zoro, wano, kaido, onigashima\n"
            "Cluster 1 Keywords: isekai, reincarnation, hero, demon, king\n\n"
            "EXAMPLE JSON OUTPUT:\n"
            '{\n'
            '  "0": "One Piece: Wano Arc",\n'
            '  "1": "Isekai & Reincarnation Tropes"\n'
            '}\n\n'
            "Now, generate the titles for the following input:\n"
            f"{prompt_input}"
        )

        try:
            response_str = self.llm_service.get_simple_response(prompt)
            if response_str and not response_str.startswith("Error:"):
                # Clean up the response to extract only the JSON part
                json_match = re.search(r'\{.*\}', response_str, re.DOTALL)
                if json_match:
                    cleaned_json_str = json_match.group(0)
                    titles_data = json.loads(cleaned_json_str)
                    # Convert keys back to integers for consistency
                    return {int(k): v for k, v in titles_data.items()}
                else:
                    logger.warning("LLM batch title generation did not return a valid JSON object.")
            else:
                 logger.error(f"LLM call for batch titles failed. Response: {response_str}")
        except Exception as e:
            logger.error(f"Failed to generate or parse LLM titles in batch: {e}", exc_info=True)

        # Fallback if LLM fails
        return {cid: ", ".join(kw[:3]).capitalize() for cid, kw in all_keywords.items()}


    def perform_kmeans_clustering(self, n_clusters: int = 5) -> Tuple[List[Dict[str, Any]], Dict[int, Any]]:
        all_documents = self.vector_store.get_all_documents_with_embeddings()
        if not all_documents: return [], {}

        embeddings = [np.array(doc["embedding"]) for doc in all_documents if doc.get("embedding") is not None]
        if not embeddings: return [], {}

        valid_docs = [doc for doc in all_documents if doc.get("embedding") is not None]
        embeddings_array = np.array(embeddings)

        if n_clusters > len(embeddings_array): n_clusters = len(embeddings_array)
        if n_clusters == 0: return [], {}

        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            cluster_labels = kmeans.fit_predict(embeddings_array)

            closest_docs_indices, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, embeddings_array)
            clustered_docs_by_label = [[] for _ in range(n_clusters)]
            for i, doc in enumerate(valid_docs):
                label = int(cluster_labels[i])
                doc['cluster_label'] = label
                clustered_docs_by_label[label].append(doc)

            all_cluster_keywords = self._get_top_terms_for_all_clusters(clustered_docs_by_label)
            all_cluster_titles = self._get_llm_cluster_titles_in_batch(all_cluster_keywords)

            cluster_info = {}
            for i in range(n_clusters):
                representative_doc_index = closest_docs_indices[i]
                representative_doc = valid_docs[representative_doc_index]

                cluster_info[i] = {
                    "title": all_cluster_titles.get(i, "Untitled Cluster"),
                    "document_count": len(clustered_docs_by_label[i]),
                    "top_terms": all_cluster_keywords.get(i, []),
                    "representative_image": representative_doc.get("metadata", {}).get("poster_url")
                }

            logger.info(f"Successfully clustered {len(valid_docs)} documents into {n_clusters} clusters.")
            return valid_docs, cluster_info
        except Exception as e:
            logger.error(f"Error during clustering: {e}", exc_info=True)
            return [], {}
