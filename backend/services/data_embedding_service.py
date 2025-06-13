# backend/services/data_embedding_service.py
import logging
import time # Import time for sleep
from typing import List, Dict, Any, Tuple

# REMOVED: Circular import - global instances are passed via constructor.
# from globals import global_vector_store, global_ollama_embedder

# Import services that fetch raw data
from services.one_piece_api_service import OnePieceAPIService
from controllers.news_controller import NewsController # ANN Recent is now via NewsController
from controllers.aniwatch_controller import AniwatchController # Import the new AniwatchController

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
        # Initialize AniwatchController
        self.aniwatch_controller = AniwatchController()
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
        logging.debug(f"DataEmbeddingService: Starting ANN summary data embedding (limit={limit})...")
        # NewsController's get_recent_news_articles already handles XML parsing and returns data, status
        articles_data, status_code = self.news_controller.get_recent_news_articles(limit=limit)

        if status_code == 200 and articles_data:
            for article in articles_data:
                item_id = article.get('id')
                item_type = article.get('type')
                item_name = article.get('name')
                item_precision = article.get('precision')

                # Construct content for embedding. Prioritize 'name' and 'type'.
                content = f"Anime News Network: Type: {item_type}, Name: {item_name}, Precision: {item_precision}."
                metadata = {
                    "source": "ann_recent_item_summary",
                    "id": item_id,
                    "type": item_type,
                    "name": item_name,
                    "precision": item_precision,
                }
                self.embed_text_data(content, metadata)
            logging.info(f"DataEmbeddingService: Embedded {len(articles_data)} ANN recent item summaries.")
        else:
            if status_code == 200:
                logging.info("DataEmbeddingService: ANN summary data retrieval successful, but no recent items were found.")
            else:
                error_message = articles_data.get('error', 'Unknown error content') if isinstance(articles_data, dict) else 'Non-dict error response from NewsController'
                logging.warning(f"DataEmbeddingService: Failed to retrieve ANN summary data. Status code: {status_code}, Error: {error_message}")

        logging.debug("DataEmbeddingService: Finished ANN summary data embedding.")

    def embed_ann_details_data(self, limit: int = 100) -> Tuple[int, int]:
        """
        Fetches detailed ANN encyclopedia data (anime/manga) and embeds it.
        This performs a two-step process: get recent IDs, then fetch details for each.
        Includes a delay to respect API rate limits.
        Returns: (processed_count, failed_count)
        """
        logging.info(f"DataEmbeddingService: Starting ANN detailed data embedding for {limit} recent items...")
        processed_count = 0
        failed_count = 0

        # Step 1: Get a list of recent encyclopedia items (anime/manga types)
        recent_items, status_code = self.news_controller.get_recent_news_articles(limit=limit)

        if status_code != 200 or not recent_items:
            logging.error(f"DataEmbeddingService: Failed to get recent ANN items. Status: {status_code}, Data: {recent_items}")
            # If the initial fetch fails, consider all requested items as failed for the purpose of the return count
            return processed_count, limit

        logging.info(f"DataEmbeddingService: Retrieved {len(recent_items)} recent ANN items for detailed processing.")

        for i, item_summary in enumerate(recent_items):
            item_id = item_summary.get('id')
            item_name = item_summary.get('name')
            item_type = item_summary.get('type') # e.g., 'anime', 'manga', 'TV', 'OAV'

            if not item_id:
                logging.warning(f"DataEmbeddingService: Skipping item due to missing ID: {item_summary}")
                failed_count += 1
                continue

            # Respect ANN API rate limits (0.5 seconds between requests)
            if i > 0: # Don't sleep before the very first request
                time.sleep(0.5)

            # Step 2: Fetch detailed information for each item
            details, details_status_code = self.news_controller.get_ann_title_details(int(item_id))

            if details_status_code == 200 and details:
                # Construct comprehensive content for embedding
                content_parts = []
                content_parts.append(f"Title: {details.get('main_title', item_name)}")
                content_parts.append(f"Type: {details.get('type', item_type)}")
                if details.get('episodes') is not None:
                    content_parts.append(f"Episodes: {details.get('episodes')}")
                if details.get('vintage'):
                    content_parts.append(f"Aired/Released: {details.get('vintage')}")
                if details.get('genres'):
                    content_parts.append(f"Genres: {', '.join(details.get('genres'))}")
                if details.get('themes'):
                    content_parts.append(f"Themes: {', '.join(details.get('themes'))}")
                if details.get('alternative_titles'):
                    content_parts.append(f"Alternative Titles: {', '.join(details.get('alternative_titles'))}")
                if details.get('description'): # This is the 'Plot Summary'
                    content_parts.append(f"Description: {details.get('description')}")
                if details.get('staff'):
                    staff_info = [f"{s.get('person')} ({s.get('task')})" for s in details.get('staff')]
                    content_parts.append(f"Staff: {', '.join(staff_info)}")
                if details.get('related_titles'):
                    related_info = [f"{r.get('name', r.get('id'))} ({r.get('relation')})" for r in details.get('related_titles')]
                    content_parts.append(f"Related: {', '.join(related_info)}")


                full_content = ". ".join([p for p in content_parts if p]) # Join with period for better readability/embedding

                # Create metadata for the vector store
                metadata = {
                    "source": "ann_details",
                    "id": details.get('id'),
                    "main_title": details.get('main_title'),
                    "type": details.get('type'),
                    "genres": details.get('genres'),
                    "vintage": details.get('vintage'),
                    "episodes": details.get('episodes')
                    # Do NOT include the full description in metadata to avoid redundancy and large object sizes
                }
                self.embed_text_data(full_content, metadata)
                processed_count += 1
            else:
                logging.warning(f"DataEmbeddingService: Failed to get details for ANN item ID {item_id}. Status: {details_status_code}, Error: {details.get('error', 'Unknown error')}")
                failed_count += 1

        logging.info(f"DataEmbeddingService: Finished ANN detailed data embedding. Processed {processed_count}, Failed {failed_count}.")
        return processed_count, failed_count

    def embed_aniwatch_data(self, limit: int = 100, page_limit: int = 5) -> Tuple[int, int]:
        """
        Fetches detailed Aniwatch anime data and embeds it into the vector store.
        This performs a two-step process: get A-Z list (for IDs), then fetch about info for each.
        Includes a delay to respect API rate limits.
        Returns: (processed_count, failed_count)
        """
        logging.info(f"DataEmbeddingService: Starting Aniwatch detailed data embedding for {limit} items (across {page_limit} pages)...")
        processed_count = 0
        failed_count = 0
        total_items_to_process = 0

        # Aniwatch API's A-Z list has sort options; we'll fetch from 'all'
        # Iterate through pages to get a sufficient number of anime IDs
        all_anime_ids = []
        for page_num in range(1, page_limit + 1):
            aniwatch_list_data, status_code = self.aniwatch_controller.get_aniwatch_az_list_data(
                sort_option="all", page=page_num
            )
            if status_code != 200 or not aniwatch_list_data or not aniwatch_list_data.get("animes"):
                logging.warning(f"DataEmbeddingService: Failed to get Aniwatch A-Z list page {page_num}. Status: {status_code}, Data: {aniwatch_list_data}")
                break # Stop if a page fails or no more anime

            for anime_summary in aniwatch_list_data["animes"]:
                if anime_summary.get("id"):
                    all_anime_ids.append(anime_summary["id"])
                    if len(all_anime_ids) >= limit:
                        break # Stop collecting IDs if limit is reached

            if len(all_anime_ids) >= limit or not aniwatch_list_data.get("hasNextPage"):
                break # Stop if limit is reached or no more pages

            time.sleep(0.2) # Small delay between page fetches

        total_items_to_process = min(limit, len(all_anime_ids))
        logging.info(f"DataEmbeddingService: Collected {total_items_to_process} Aniwatch anime IDs for detailed processing.")

        for i, anime_id in enumerate(all_anime_ids[:limit]): # Process up to the specified limit
            if i > 0:
                time.sleep(0.5) # Delay between individual detail fetches to respect API limits

            details, details_status_code = self.aniwatch_controller.get_aniwatch_anime_details_data(anime_id)

            if details_status_code == 200 and details:
                content_parts = []
                content_parts.append(f"Title: {details.get('name')}")
                if details.get('japanese_name'):
                    content_parts.append(f"Japanese Title: {details.get('japanese_name')}")
                content_parts.append(f"Type: {details.get('type')}")
                if details.get('synopsis'):
                    content_parts.append(f"Synopsis: {details.get('synopsis')}")
                if details.get('genres'):
                    content_parts.append(f"Genres: {', '.join(details.get('genres'))}")
                if details.get('aired'):
                    content_parts.append(f"Aired: {details.get('aired')}")
                if details.get('status'):
                    content_parts.append(f"Status: {details.get('status')}")
                if details.get('studios'):
                    content_parts.append(f"Studios: {', '.join(details.get('studios'))}")
                if details.get('total_episodes') is not None:
                    content_parts.append(f"Total Episodes: {details.get('total_episodes')}")
                if details.get('duration'):
                    content_parts.append(f"Duration: {details.get('duration')}")
                if details.get('rating'):
                    content_parts.append(f"Rating: {details.get('rating')}")
                if details.get('score') is not None:
                    content_parts.append(f"Score: {details.get('score')}")
                if details.get('producers'):
                    content_parts.append(f"Producers: {', '.join(details.get('producers'))}")
                if details.get('relations'):
                    relation_info = [f"{r.get('name', r.get('id'))} ({r.get('type')})" for r in details.get('relations')]
                    content_parts.append(f"Relations: {', '.join(relation_info)}")
                if details.get('recommendations'):
                    rec_info = [f"{r.get('name', r.get('id'))} (Recommended)" for r in details.get('recommendations')]
                    content_parts.append(f"Recommendations: {', '.join(rec_info)}")


                full_content = ". ".join([p for p in content_parts if p])

                metadata = {
                    "source": "aniwatch_details",
                    "id": details.get('id'),
                    "name": details.get('name'),
                    "type": details.get('type'),
                    "genres": details.get('genres'),
                    "aired": details.get('aired'),
                    "total_episodes": details.get('total_episodes'),
                    "rating": details.get('rating'),
                    "score": details.get('score')
                    # Synopsis is part of content, not metadata to avoid large metadata
                }
                self.embed_text_data(full_content, metadata)
                processed_count += 1
            else:
                logging.warning(f"DataEmbeddingService: Failed to get details for Aniwatch anime ID {anime_id}. Status: {details_status_code}, Error: {details.get('error', 'Unknown error')}")
                failed_count += 1

        logging.info(f"DataEmbeddingService: Finished Aniwatch detailed data embedding. Processed {processed_count}, Failed {failed_count}.")
        return processed_count, failed_count


    def embed_all_data(self):
        """Orchestrates the embedding of data from all configured sources."""
        logging.debug("DataEmbeddingService: Starting embedding of all data...")
        # Clear existing documents in the vector store before re-embedding,
        # especially important for in-memory store in development to prevent duplicates
        self.vector_store.documents = []
        logging.info("VectorStore: Cleared existing documents for fresh embedding.")

        self.embed_one_piece_data()
        self.embed_ann_details_data(limit=100) # Call the new detailed embedding method
        self.embed_aniwatch_data(limit=100, page_limit=5) # Call the new Aniwatch embedding method
        logging.debug("DataEmbeddingService: All data embedding complete.")

