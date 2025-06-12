# backend/embeddings/vector_store.py
import numpy as np
import pickle # For saving/loading Python objects
import gzip   # For compression
import os     # For file path operations
import logging
from typing import List, Dict, Optional, Any

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
            logger.error(f"VectorStore: Invalid embedding type. Expected list of floats, got {type(embedding)}.")
            return

        doc = {
            "id": self.next_id,
            "content": content,
            "embedding": np.array(embedding), # Store as numpy array for efficiency
            "metadata": metadata if metadata is not None else {}
        }
        self.documents.append(doc)
        self.next_id += 1
        logger.debug(f"VectorStore: Added document with ID {doc['id']}. Content snippet: '{content[:50]}...'")

    def get_document_by_id(self, doc_id: int) -> Optional[Dict]:
        """Retrieves a document by its ID."""
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        return None

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Performs a cosine similarity search against stored embeddings.

        Args:
            query_embedding (List[float]): The embedding of the query.
            top_k (int): The number of top similar documents to return.

        Returns:
            List[Dict]: A list of dictionaries, each containing 'document' and 'similarity'.
        """
        if not self.documents:
            return []

        query_vec = np.array(query_embedding)
        similarities = []

        for doc in self.documents:
            # Ensure the document embedding is a numpy array
            doc_vec = doc["embedding"]
            if doc_vec.ndim == 1 and query_vec.ndim == 1:
                similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
                similarities.append({"document": doc, "similarity": similarity})
            else:
                logger.warning(f"VectorStore: Mismatched dimensions for document ID {doc['id']}. Skipping similarity calculation.")
                continue

        # Sort by similarity in descending order
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    def get_all_documents_with_embeddings(self) -> List[Dict[str, Any]]:
        """
        Returns all stored documents, including their content, embedding, and metadata.
        The embedding will be a NumPy array.
        """
        return self.documents

    def save(self):
        """Saves the current state of the vector store to the configured .pkl.gz file."""
        if not self.db_path:
            logger.error("VectorStore: Cannot save, db_path is not configured.")
            return

        # Prepare data for saving: convert numpy arrays back to lists if needed for serialization robustness
        # (Though pickle generally handles numpy arrays, explicitly converting can prevent issues with other formats)
        serializable_documents = []
        for doc in self.documents:
            serializable_doc = doc.copy()
            if isinstance(serializable_doc.get("embedding"), np.ndarray):
                serializable_doc["embedding"] = serializable_doc["embedding"].tolist()
            serializable_documents.append(serializable_doc)

        data = {"documents": serializable_documents, "next_id": self.next_id}
        try:
            with gzip.open(self.db_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"VectorStore: Successfully saved {len(self.documents)} documents to {self.db_path}.")
        except Exception as e:
            logger.error(f"VectorStore: Failed to save vector store to {self.db_path}: {e}")

    def load(self):
        """Loads the vector store from the configured .pkl.gz file."""
        if not os.path.exists(self.db_path):
            logger.warning(f"VectorStore: No existing vector store found at {self.db_path}. Starting fresh.")
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
