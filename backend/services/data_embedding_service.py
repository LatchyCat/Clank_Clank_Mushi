# backend/services/data_embedding_service.py
import logging
import json
import os
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

from controllers.anime_controller import AnimeController
from services.one_piece_api_service import OnePieceAPIService

logger = logging.getLogger(__name__)
ERROR_LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'embedding_errors.json')

class DataEmbeddingService:
    def __init__(self, vector_store, embedder, anime_controller: AnimeController):
        self.vector_store = vector_store
        self.embedder = embedder
        self.anime_controller = anime_controller
        self.one_piece_api_service = OnePieceAPIService()
        # This will hold aggregated errors during a run
        self.error_summary = defaultdict(lambda: {'count': 0, 'examples': []})
        logger.debug("DataEmbeddingService: Initialized.")

    def _log_error(self, error_key: str, item_id: str, details: str = ""):
        """Aggregates errors to be written to a file at the end."""
        self.error_summary[error_key]['count'] += 1
        if len(self.error_summary[error_key]['examples']) < 5: # Log up to 5 examples
            self.error_summary[error_key]['examples'].append(f"ID: {item_id}, Details: {details}")

    def _write_error_log(self):
        """Writes the aggregated error summary to the JSON file."""
        if not self.error_summary:
            return

        # Sort errors by count, descending
        sorted_errors = dict(sorted(self.error_summary.items(), key=lambda item: item[1]['count'], reverse=True))

        try:
            with open(ERROR_LOG_FILE, 'w') as f:
                json.dump(sorted_errors, f, indent=2)
            logger.warning(f"Embedding process completed with errors. See '{ERROR_LOG_FILE}' for summary.")
        except Exception as e:
            logger.error(f"Failed to write to error log file: {e}")

    def _clean_id(self, raw_id: Any) -> Optional[str]:
        if raw_id is None: return None
        return str(raw_id).strip()

    def embed_text_data(self, content: str, metadata: Dict[str, Any], source_item_id: str) -> bool:
        if self.vector_store.get_document_by_source_id(source_item_id):
            return True
        embedding = self.embedder.embed_text(content)
        if embedding:
            self.vector_store.add_document(content, embedding, metadata, source_item_id)
            return True
        self._log_error("Embedding Generation Failed", source_item_id, f"Ollama embedder returned None for title: {metadata.get('title')}")
        return False

    def _process_and_embed_anime_item(self, item: Dict, source_type: str) -> bool:
        anime_id = self._clean_id(item.get('id'))
        if not anime_id:
            self._log_error("Missing Anime ID", "N/A", f"Source: {source_type}, Item: {item}")
            return False

        # --- FAULT TOLERANT DETAIL FETCHING ---
        details, status_code = self.anime_controller.get_anime_details_data(anime_id)
        if status_code != 200:
            self._log_error(f"Main Detail Fetch Failed (Status {status_code})", anime_id, f"Source: {source_type}")
            return False

        title = details.get('title')
        if not title:
            self._log_error("Missing Title in Details", anime_id, f"Source: {source_type}")
            return False

        # Construct a rich document for embedding
        content_parts = [
            f"Title: {title}",
            f"Japanese Title: {details.get('japanese_title', 'N/A')}",
            f"Type: {details.get('show_type', 'N/A')}",
            f"Status: {details.get('status', 'N/A')}",
            f"Genres: {', '.join(details.get('genres', []))}",
            f"Synopsis: {details.get('synopsis', 'No synopsis available.')}"
        ]
        content = "\n".join(content_parts)

        metadata = {
            "source": "Anime API",
            "type": "anime_details",
            "title": title,
            "anime_id": anime_id  # This is crucial for route-safe linking
        }

        source_item_id = f"anime_api_details_{anime_id}"
        return self.embed_text_data(content, metadata, source_item_id)

    def embed_one_piece_data(self) -> Tuple[int, int]:
        logger.info("Starting One Piece data embedding...")
        processed, failed = 0, 0

        op_sources = {
            "characters": self.one_piece_api_service.get_characters,
            "fruits": self.one_piece_api_service.get_fruits
        }

        for source_name, fetch_func in op_sources.items():
            data, status = fetch_func()
            if status == 200 and data:
                for item in data:
                    item_id = self._clean_id(item.get('id'))
                    name = item.get('name')
                    if item_id and name:
                        content = f"One Piece {source_name[:-1]}: {name}. Description: {item.get('description', 'N/A')}"
                        metadata = {"source": "One Piece API", "type": f"one_piece_{source_name[:-1]}", "title": name}
                        if self.embed_text_data(content, metadata, f"one_piece_{source_name[:-1]}_{item_id}"):
                            processed += 1
                        else:
                            failed += 1
                    else:
                        failed += 1
                        self._log_error("Missing ID or Name", f"op_{source_name}", str(item))
            else:
                logger.error(f"Failed to fetch One Piece {source_name}. Status: {status}")
                self._log_error(f"One Piece API Call Failed", source_name, f"Status code: {status}")

        logger.info(f"Finished One Piece data embedding. Processed: {processed}, Failed: {failed}.")
        return processed, failed

    def embed_from_anime_api_list(self, section_name: str, items_list: List[Dict]) -> Tuple[int, int]:
        processed, failed = 0, 0
        if not isinstance(items_list, list):
            self._log_error("Invalid Item List", section_name, f"Expected a list, got {type(items_list)}")
            return 0, 0

        for item in items_list:
            if self._process_and_embed_anime_item(item, section_name):
                processed += 1
            else:
                failed += 1
        return processed, failed

    def embed_all_data(self):
        logger.info("Starting embedding of all data sources...")
        if os.path.exists(ERROR_LOG_FILE):
            os.remove(ERROR_LOG_FILE)
        self.error_summary.clear()

        self.vector_store.load()
        total_processed, total_failed = 0, 0

        p, f = self.embed_one_piece_data()
        total_processed += p; total_failed += f

        home_data, status = self.anime_controller.anime_api_service.get_home_info()
        if status == 200 and home_data.get('success'):
            results = home_data.get('results', {})
            for section in ['spotlights', 'trending', 'topAiring', 'mostPopular', 'mostFavorite']:
                logger.info(f"--- Embedding Anime API Section: {section} ---")
                p, f = self.embed_from_anime_api_list(section, results.get(section, []))
                total_processed += p; total_failed += f
        else:
            self._log_error("Home API Call Failed", "N/A", f"Status: {status}")

        common_categories = ["top-airing", "most-popular", "completed", "movie", "tv", "genre/action"]
        for category in common_categories:
            logger.info(f"--- Embedding Anime API Category: {category} ---")
            cat_data, status = self.anime_controller.anime_api_service.get_anime_by_category(category, limit=25)
            if status == 200 and cat_data.get('success'):
                p, f = self.embed_from_anime_api_list(f"category_{category}", cat_data.get('results', {}).get('data', []))
                total_processed += p; total_failed += f
            else:
                self._log_error(f"Category Fetch Failed", category, f"Status: {status}")

        logger.info("--- Data Embedding Summary ---")
        logger.info(f"Total Processed/Updated: {total_processed}")
        logger.info(f"Total Failed Items: {total_failed}")

        self._write_error_log()
        self.vector_store.save()
