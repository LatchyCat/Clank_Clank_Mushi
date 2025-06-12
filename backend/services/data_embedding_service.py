# backend/services/data_embedding_service.py
import logging
from typing import List, Dict, Any

# Import global instances from the new globals.py module
from globals import global_vector_store, global_ollama_embedder

# Import services that fetch raw data
from services.one_piece_api_service import OnePieceAPIService
from controllers.news_controller import NewsController # ANN Recent is now via NewsController

class DataEmbeddingService:
    """
    Handles the process of fetching data from various sources,
    transforming it into suitable text format, and embedding it
    into the vector store.
    """

    def __init__(self, vector_store, embedder):
        self.vector_store = vector_store
        self.embedder = embedder
        self.one_piece_api_service = OnePieceAPIService()
        # Initialize NewsController to get ANN recent items
        self.news_controller = NewsController()
        logging.debug("DataEmbeddingService: Initialized.")

    def embed_text_data(self, content: str, metadata: Dict[str, Any]):
        """Embeds a single piece of text content with its metadata."""
        try:
            embedding = self.embedder.embed_text(content)
            if embedding is not None:
                self.vector_store.add_document(content, embedding, metadata)
                # logging.debug(f"VectorStore: Added document with ID {len(self.vector_store.documents) - 1}.")
                # More detailed log for content preview
                logging.debug(f"VectorStore: Added document from '{metadata.get('source', 'unknown')}' - Preview: '{content[:50]}...'")
            else:
                logging.warning(f"Could not generate embedding for content (first 50 chars): '{content[:50]}...'")
        except Exception as e:
            logging.error(f"Error embedding document (first 50 chars: '{content[:50]}...'): {e}")

    def embed_one_piece_data(self):
        """Fetches and embeds One Piece data (sagas, characters, fruits)."""
        logging.debug("DataEmbeddingService: Starting One Piece data embedding...")

        # Embed Sagas
        sagas_data = self.one_piece_api_service.get_all_sagas()
        if sagas_data:
            for saga in sagas_data:
                content = f"One Piece Saga: {saga.get('title')}. Number of arcs: {saga.get('number_of_arcs')}."
                metadata = {"source": "one_piece_saga", "title": saga.get('title'), "id": saga.get('id')}
                self.embed_text_data(content, metadata)
            logging.info(f"DataEmbeddingService: Embedded {len(sagas_data)} One Piece sagas.")
        else:
            logging.warning("DataEmbeddingService: Failed to retrieve One Piece sagas or no sagas found.")

        # Embed Characters
        characters_data = self.one_piece_api_service.get_all_characters()
        if characters_data:
            for char in characters_data:
                content = f"One Piece Character: {char.get('name')}. Gender: {char.get('gender')}. Status: {char.get('status')}."
                metadata = {"source": "one_piece_character", "name": char.get('name'), "id": char.get('id')}
                self.embed_text_data(content, metadata)
            logging.info(f"DataEmbeddingService: Embedded {len(characters_data)} One Piece characters.")
        else:
            logging.warning("DataEmbeddingService: Failed to retrieve One Piece characters or no characters found.")

        # Embed Fruits (Devil Fruits)
        fruits_data = self.one_piece_api_service.get_all_fruits()
        if fruits_data:
            for fruit in fruits_data:
                content = f"One Piece Devil Fruit: {fruit.get('name')}. Type: {fruit.get('type')}. Description: {fruit.get('description')}."
                metadata = {"source": "one_piece_fruit", "name": fruit.get('name'), "id": fruit.get('id')}
                self.embed_text_data(content, metadata)
            logging.info(f"DataEmbeddingService: Embedded {len(fruits_data)} One Piece fruits.")
        else:
            logging.warning("DataEmbeddingService: Failed to retrieve One Piece fruits or no fruits found.")

        logging.debug("DataEmbeddingService: Finished One Piece data embedding.")


    def embed_ann_data(self, limit: int = 20):
        """
        Fetches and embeds recent items from the Anime News Network (ANN) API.
        This uses the NewsController to get structured data.
        """
        logging.debug(f"DataEmbeddingService: Starting ANN data embedding (limit={limit})...")
        # NewsController's get_recent_news_articles already handles XML parsing and returns data, status
        articles_data, status_code = self.news_controller.get_recent_news_articles(limit=limit)

        if status_code == 200 and articles_data:
            for article in articles_data:
                item_id = article.get('id')
                item_type = article.get('type')
                item_name = article.get('name')
                item_precision = article.get('precision')
                # Removed 'item_link' as it's not present in reports.xml

                # Construct content for embedding. Prioritize 'name' and 'type'.
                content = f"Anime News Network: Type: {item_type}, Name: {item_name}, Precision: {item_precision}."
                # Removed conditional addition of link to content

                metadata = {
                    "source": "ann_recent_item",
                    "id": item_id,
                    "type": item_type,
                    "name": item_name,
                    "precision": item_precision,
                    # Removed 'link' from metadata
                }
                self.embed_text_data(content, metadata)
            logging.info(f"DataEmbeddingService: Embedded {len(articles_data)} ANN recent items.")
        else:
            # Differentiate between no articles found (but successful request) and actual API error
            if status_code == 200: # No articles found, but request was successful
                logging.info("DataEmbeddingService: ANN data retrieval successful, but no recent items were found.")
            else: # An actual error occurred, and articles_data should be a dict
                error_message = articles_data.get('error', 'Unknown error content') if isinstance(articles_data, dict) else 'Non-dict error response from NewsController'
                logging.warning(f"DataEmbeddingService: Failed to retrieve ANN data. Status code: {status_code}, Error: {error_message}")

        logging.debug("DataEmbeddingService: Finished ANN data embedding.")


    def embed_all_data(self):
        """Orchestrates the embedding of data from all configured sources."""
        logging.debug("DataEmbeddingService: Starting embedding of all data...")
        # Clear existing documents in the vector store before re-embedding,
        # especially important for in-memory store in development to prevent duplicates
        self.vector_store.documents = []
        logging.info("VectorStore: Cleared existing documents for fresh embedding.")

        self.embed_one_piece_data()
        self.embed_ann_data() # You can pass a limit here if you want fewer ANN items
        logging.debug("DataEmbeddingService: All data embedding complete.")
