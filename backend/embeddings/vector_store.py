# backend/embeddings/vector_store.py
import numpy as np
import pickle # For saving/loading Python objects
import gzip   # For compression
import os     # For file path operations
import logging
from typing import List, Dict, Optional, Any, Tuple # Added Tuple for similarity_search return type

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

    def add_document(self, content: str, embedding: List[float], metadata: Optional[Dict] = None, source_item_id: Optional[str] = None):
        """
        Adds a document to the vector store, checking for duplicates by source_item_id.

        Args:
            content (str): The original text content of the document.
            embedding (List[float]): The embedding vector of the content.
            metadata (Optional[Dict]): Optional dictionary of additional metadata for the document.
            source_item_id (Optional[str]): A unique identifier from the original data source to prevent duplicates.
        """
        # Ensure embedding is a numpy array for consistent operations
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding)

        # Check for duplicate source_item_id to prevent re-embedding the same item
        if source_item_id:
            if any(doc.get("source_item_id") == source_item_id for doc in self.documents):
                logger.debug(f"VectorStore: Document with source_item_id '{source_item_id}' already exists. Skipping.")
                return

        document = {
            "id": self.next_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata if metadata is not None else {},
            "source_item_id": source_item_id
        }
        self.documents.append(document)
        self.next_id += 1
        logger.debug(f"VectorStore: Added document ID {document['id']} (Source ID: {source_item_id}). Total documents: {len(self.documents)}")


    def get_document_by_source_id(self, source_item_id: str) -> Optional[Dict]:
        """
        Retrieves a document by its source_item_id.
        """
        for doc in self.documents:
            if doc.get("source_item_id") == source_item_id:
                return doc
        return None

    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a cosine similarity search against stored document embeddings.

        Args:
            query_embedding (List[float]): The embedding vector of the query.
            top_k (int): The number of top similar documents to return.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary is a document
                        augmented with a 'similarity_score'. Sorted by score descending.
        """
        if not self.documents or not query_embedding:
            logger.warning("VectorStore: No documents or query embedding for similarity search.")
            return []

        query_embedding_array = np.array(query_embedding)
        if query_embedding_array.ndim == 1:
            query_embedding_array = query_embedding_array.reshape(1, -1)

        # Ensure query_embedding is a unit vector (normalized)
        norm_query_embedding = query_embedding_array / np.linalg.norm(query_embedding_array, axis=1, keepdims=True)

        scores = []
        for doc in self.documents:
            doc_embedding = doc.get("embedding")
            # Ensure embedding is a numpy array before performing calculations
            if isinstance(doc_embedding, list):
                doc_embedding = np.array(doc_embedding)

            if doc_embedding is not None and isinstance(doc_embedding, np.ndarray) and doc_embedding.size > 0:
                # Ensure document embedding is a unit vector (normalized)
                norm_doc_embedding = doc_embedding / np.linalg.norm(doc_embedding)

                # Reshape if necessary to perform dot product
                if norm_doc_embedding.ndim == 1:
                    norm_doc_embedding = norm_doc_embedding.reshape(1, -1)

                similarity = np.dot(norm_query_embedding, norm_doc_embedding.T)[0][0]
                scores.append((similarity, doc))
            else:
                logger.warning(f"VectorStore: Skipping document ID {doc.get('id')} due to missing or invalid embedding for similarity search.")

        # Sort by similarity score in descending order
        scores.sort(key=lambda x: x[0], reverse=True)

        # Return top_k documents with their scores
        result = []
        for score, doc in scores[:top_k]:
            doc_copy = doc.copy()
            doc_copy['similarity_score'] = float(score) # Ensure score is standard float
            result.append(doc_copy)

        logger.debug(f"VectorStore: Found {len(result)} relevant documents.")
        return result

    def get_all_documents_with_embeddings(self) -> List[Dict[str, Any]]:
        """
        Returns all documents currently in the store, ensuring embeddings are NumPy arrays.
        """
        return [doc for doc in self.documents if doc.get('embedding') is not None]

    def save(self):
        """
        Saves the current state of the vector store to a gzipped pickle file.
        Converts numpy arrays to lists for serialization if necessary.
        """
        try:
            # Prepare documents for serialization: convert numpy arrays to lists
            serializable_documents = []
            for doc in self.documents:
                doc_copy = doc.copy()
                if isinstance(doc_copy.get("embedding"), np.ndarray):
                    doc_copy["embedding"] = doc_copy["embedding"].tolist()
                serializable_documents.append(doc_copy)

            data_to_save = {
                "documents": serializable_documents,
                "next_id": self.next_id
            }
            with gzip.open(self.db_path, 'wb') as f:
                pickle.dump(data_to_save, f)
            logger.info(f"VectorStore: Successfully saved {len(self.documents)} documents to {self.db_path}. Next ID: {self.next_id}")
        except Exception as e:
            logger.error(f"VectorStore: Failed to save vector store to {self.db_path}: {e}", exc_info=True)

    def load(self):
        """
        Loads the vector store from a gzipped pickle file.
        Converts embedding lists back to numpy arrays upon loading.
        """
        if not os.path.exists(self.db_path):
            logger.warning(f"VectorStore: Database file not found at {self.db_path}. Starting fresh.")
            self.documents = []
            self.next_id = 0
            return

        try:
            with gzip.open(self.db_path, 'rb') as f:
                data = pickle.load(f)

            loaded_documents = []
            for doc in data.get("documents", []):
                # Convert embedding lists back to NumPy arrays if they were saved as lists
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

    def clear(self):
        """Clears all documents from the vector store."""
        self.documents = []
        self.next_id = 0
        logger.info("VectorStore: Cleared all documents.")
        self.save() # Save the empty state
