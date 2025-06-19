# backend/embeddings/vector_store.py
import numpy as np
import pickle
import gzip
import os
import faiss
import logging
from typing import List, Dict, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStore:
    """
    A high-performance in-memory vector store using Faiss for efficient similarity search.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.index_path = db_path.replace('.pkl.gz', '.faiss')
        self.documents: List[Dict] = []
        self.faiss_index: Optional[faiss.Index] = None
        self.dimension: Optional[int] = None
        self.next_id = 0
        self.source_id_map: Dict[str, int] = {}
        logger.info(f"VectorStore: Initializing with DB path: {self.db_path} and Faiss index: {self.index_path}")

    def _initialize_faiss_index(self, dimension: int):
        """Initializes a new Faiss index."""
        if self.dimension and self.dimension != dimension:
            logger.warning(f"VectorStore: Dimension mismatch. Current: {self.dimension}, New: {dimension}. Re-initializing.")
        self.dimension = dimension
        self.faiss_index = faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))
        logger.info(f"VectorStore: Initialized new Faiss index with dimension {self.dimension}.")

    def add_document(self, content: str, embedding: List[float], metadata: Optional[Dict] = None, source_item_id: Optional[str] = None):
        if source_item_id and self.get_document_by_source_id(source_item_id):
            logger.debug(f"Document with source_item_id '{source_item_id}' already exists. Skipping.")
            return

        doc_id = self.next_id
        embedding_np = np.array([embedding], dtype=np.float32)

        if self.faiss_index is None:
            self._initialize_faiss_index(embedding_np.shape[1])

        if self.dimension != embedding_np.shape[1]:
            logger.error(f"Dimension mismatch: Expected {self.dimension}, got {embedding_np.shape[1]}. Skipping document.")
            return

        self.faiss_index.add_with_ids(embedding_np, np.array([doc_id]))
        document = {"id": doc_id, "content": content, "embedding": embedding, "metadata": metadata or {}, "source_item_id": source_item_id}
        self.documents.append(document)

        if source_item_id:
            self.source_id_map[source_item_id] = doc_id
        self.next_id += 1

    def get_document_by_source_id(self, source_item_id: str) -> Optional[Dict]:
        """Efficiently retrieves a document by its unique source_item_id using a map."""
        doc_id = self.source_id_map.get(source_item_id)
        if doc_id is not None:
            # This is slightly inefficient but safer than assuming list index equals doc_id
            for doc in self.documents:
                if doc['id'] == doc_id:
                    return doc
        return None

    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return []

        query_vector = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.faiss_index.search(query_vector, top_k)

        results = []
        doc_map = {doc['id']: doc for doc in self.documents}
        for i, doc_id in enumerate(indices[0]):
            if doc_id != -1: # Faiss returns -1 for no result
                doc = doc_map.get(int(doc_id))
                if doc:
                    doc_copy = doc.copy()
                    doc_copy['distance'] = float(distances[0][i])
                    results.append(doc_copy)
        return results

    def save(self):
        """Saves the Faiss index and the document data (including embeddings) to disk."""
        logger.info(f"Attempting to save vector store to {self.db_path}")
        if self.faiss_index is None:
            logger.warning("Faiss index is not initialized. Nothing to save.")
            return
        try:
            faiss.write_index(self.faiss_index, self.index_path)
            # We save the full documents including their embeddings for reliability.
            data_to_save = {
                "documents": self.documents,
                "next_id": self.next_id,
                "dimension": self.dimension,
                "source_id_map": self.source_id_map
            }
            with gzip.open(self.db_path, 'wb') as f:
                pickle.dump(data_to_save, f)
            logger.info(f"Successfully saved {len(self.documents)} documents and Faiss index with {self.faiss_index.ntotal} vectors.")
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}", exc_info=True)

    def load(self):
        """Loads the Faiss index and document data from disk."""
        if not os.path.exists(self.db_path) or not os.path.exists(self.index_path):
            logger.warning("Database or Faiss index file not found. Starting fresh.")
            self.clear()
            return
        try:
            self.faiss_index = faiss.read_index(self.index_path)
            with gzip.open(self.db_path, 'rb') as f:
                data = pickle.load(f)
            self.documents = data.get("documents", [])
            self.next_id = data.get("next_id", len(self.documents))
            self.dimension = data.get("dimension") or self.faiss_index.d
            self.source_id_map = data.get("source_id_map", {})
            # Verification step
            if self.documents and 'embedding' not in self.documents[0]:
                logger.error("Loaded documents are missing embeddings! The pickle file might be from an old version. Clearing and starting fresh to prevent issues.")
                self.clear()
                return
            logger.info(f"Successfully loaded {self.faiss_index.ntotal} vectors and {len(self.documents)} documents.")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}. Starting fresh.", exc_info=True)
            self.clear()

    def get_all_documents_with_embeddings(self) -> List[Dict[str, Any]]:
        return [doc for doc in self.documents if 'embedding' in doc and doc['embedding'] is not None]

    def clear(self):
        """Clears the in-memory store and deletes the corresponding files."""
        self.documents = []
        self.faiss_index = None
        self.dimension = None
        self.next_id = 0
        self.source_id_map = {}
        if os.path.exists(self.index_path):
            try:
                os.remove(self.index_path)
            except OSError as e:
                logger.error(f"Error removing Faiss index file: {e}")
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError as e:
                logger.error(f"Error removing DB pickle file: {e}")
        logger.info("Cleared all documents and Faiss index.")
