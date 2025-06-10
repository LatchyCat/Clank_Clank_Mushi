# backend/embeddings/vector_store.py
import numpy as np
from typing import List, Dict, Optional

class VectorStore:
    """
    A simple in-memory vector store for storing documents and their embeddings.
    Provides basic similarity search using cosine similarity.
    """
    def __init__(self):
        self.documents: List[Dict] = []
        self.next_id = 0
        print("DEBUG: VectorStore: Initialized in-memory VectorStore.")

    def add_document(self, content: str, embedding: List[float], metadata: Optional[Dict] = None):
        """
        Adds a document to the vector store.

        Args:
            content (str): The original text content of the document.
            embedding (List[float]): The embedding vector of the content.
            metadata (Optional[Dict]): Optional dictionary of additional metadata for the document.
        """
        if not isinstance(embedding, list) or not all(isinstance(x, (int, float)) for x in embedding):
            print(f"ERROR: VectorStore: Invalid embedding format for document ID {self.next_id}.")
            return

        doc = {
            "id": self.next_id,
            "content": content,
            "embedding": np.array(embedding), # Store as numpy array for efficient calculations
            "metadata": metadata if metadata is not None else {}
        }
        self.documents.append(doc)
        self.next_id += 1
        print(f"DEBUG: VectorStore: Added document with ID {doc['id']}.")

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculates the cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0 # Handle zero vectors
        return dot_product / (norm_vec1 * norm_vec2)

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
            print("DEBUG: VectorStore: No documents in store to search.")
            return []

        if not isinstance(query_embedding, list) or not all(isinstance(x, (int, float)) for x in query_embedding):
            print("ERROR: VectorStore: Invalid query embedding format.")
            return []

        query_vec = np.array(query_embedding)
        similarities = []

        for doc in self.documents:
            score = self._cosine_similarity(query_vec, doc["embedding"])
            similarities.append({
                "document": doc,
                "similarity_score": float(score) # Convert numpy float to Python float
            })

        # Sort by similarity score in descending order and return top_k
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        print(f"DEBUG: VectorStore: Found {len(similarities)} similarities, returning top {top_k}.")
        return similarities[:top_k]
