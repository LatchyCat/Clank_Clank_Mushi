# backend/embeddings/vector_store.py
import numpy as np
import pickle # For saving/loading Python objects
import gzip   # For compression
import os     # For file path operations
import logging
from typing import List, Dict, Optional

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStore:
    """
    A simple in-memory vector store for storing documents and their embeddings.
    Provides basic similarity search using cosine similarity.
    Supports persistence to a .pkl.gz file.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.documents: List[Dict] = []
        self.next_id = 0
        logger.info(f"VectorStore: Initializing VectorStore with persistence path: {self.db_path}")
        self.load() # Attempt to load existing data on initialization

    def add_document(self, content: str, embedding: List[float], metadata: Optional[Dict] = None):
        """
        Adds a document to the vector store.

        Args:
            content (str): The original text content of the document.
            embedding (List[float]): The embedding vector of the content.
            metadata (Optional[Dict]): Optional dictionary of additional metadata for the document.
        """
        if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
            logger.error(f"VectorStore: Invalid embedding format for document ID {self.next_id}.")
            return

        doc = {
            "id": self.next_id,
            "content": content,
            "embedding": np.array(embedding), # Store as numpy array for efficient calculations
            "metadata": metadata if metadata is not None else {}
        }
        self.documents.append(doc)
        # Ensure next_id is always greater than the max existing ID to avoid collisions
        # This is important if documents are loaded from disk with arbitrary IDs
        if self.documents: # Only update next_id if there are documents
            self.next_id = max(self.next_id, doc["id"] + 1)
        else: # If no documents, start from 0
            self.next_id = 0
        logger.debug(f"VectorStore: Added document with ID {doc['id']}.")

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculates the cosine similarity between two vectors."""
        # Ensure vec1 and vec2 are numpy arrays for consistency
        if not isinstance(vec1, np.ndarray):
            vec1 = np.array(vec1)
        if not isinstance(vec2, np.ndarray):
            vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        if norm_a == 0 or norm_b == 0:
            return 0.0 # Avoid division by zero
        return dot_product / (norm_a * norm_b)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Searches for the top_k most similar documents to the query embedding.

        Args:
            query_embedding (List[float]): The embedding vector of the search query.
            top_k (int): The number of top similar documents to return.

        Returns:
            List[Dict]: A list of dictionaries, each containing 'document' (the original doc)
                        and 'similarity_score'. Sorted by similarity_score in descending order.
        """
        if not self.documents:
            logger.info("VectorStore: No documents in store to search.")
            return []

        if not isinstance(query_embedding, list) or not all(isinstance(x, (int, float)) for x in query_embedding):
            logger.error("VectorStore: Invalid query embedding format.")
            return []

        query_vec = np.array(query_embedding)
        similarities = []

        for doc in self.documents:
            # Ensure doc["embedding"] is treated as a numpy array for calculation
            doc_embedding_np = doc["embedding"] if isinstance(doc["embedding"], np.ndarray) else np.array(doc["embedding"])
            score = self._cosine_similarity(query_vec, doc_embedding_np)
            similarities.append({
                "document": doc,
                "similarity_score": float(score) # Convert numpy float to Python float
            })

        # Sort by similarity score in descending order and return top_k
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        logger.debug(f"VectorStore: Found {len(similarities)} similarities, returning top {top_k}.")
        return similarities[:top_k]

    def save(self):
        """
        Saves the current state of the vector store (documents and next_id) to a gzipped pickle file.
        NumPy arrays are converted to lists for pickling.
        """
        try:
            # Convert NumPy arrays in documents to lists for pickling
            serializable_documents = []
            for doc in self.documents:
                # Create a copy to avoid modifying the original documents in memory
                serializable_doc = doc.copy()
                if isinstance(serializable_doc.get("embedding"), np.ndarray):
                    serializable_doc["embedding"] = serializable_doc["embedding"].tolist()
                serializable_documents.append(serializable_doc)

            # Ensure the directory exists
            # db_path might include a filename, os.path.dirname gets the directory
            os.makedirs(os.path.dirname(self.db_path) or '.', exist_ok=True) # handle case where db_path is just a filename

            with gzip.open(self.db_path, 'wb') as f:
                pickle.dump({"documents": serializable_documents, "next_id": self.next_id}, f)
            logger.info(f"VectorStore: Successfully saved vector store to {self.db_path}")
        except Exception as e:
            logger.error(f"VectorStore: Failed to save vector store to {self.db_path}: {e}")

    def load(self):
        """
        Loads the vector store state (documents and next_id) from a gzipped pickle file.
        Lists are converted back to NumPy arrays.
        """
        if not os.path.exists(self.db_path):
            logger.info(f"VectorStore: No existing vector store found at {self.db_path}. Starting fresh.")
            self.documents = []
            self.next_id = 0
            return

        try:
            with gzip.open(self.db_path, 'rb') as f:
                data = pickle.load(f)

            loaded_documents = []
            for doc in data.get("documents", []):
                # Convert embedding lists back to NumPy arrays
                if isinstance(doc.get("embedding"), list):
                    doc["embedding"] = np.array(doc["embedding"])
                loaded_documents.append(doc)

            self.documents = loaded_documents
            self.next_id = data.get("next_id", 0)
            logger.info(f"VectorStore: Successfully loaded {len(self.documents)} documents from {self.db_path}.")
            if self.documents:
                # Recalculate next_id to ensure it's correct even if not perfectly saved or if IDs are not sequential
                self.next_id = max([doc["id"] for doc in self.documents]) + 1
                logger.info(f"VectorStore: Recalculated next_id to {self.next_id} after loading.")

        except EOFError:
            logger.warning(f"VectorStore: {self.db_path} is empty or corrupted (EOFError). Starting fresh.")
            self.documents = []
            self.next_id = 0
        except Exception as e:
            logger.error(f"VectorStore: Failed to load vector store from {self.db_path}: {e}. Starting fresh.")
            self.documents = []
            self.next_id = 0
