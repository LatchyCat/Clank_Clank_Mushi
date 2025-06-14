# backend/services/data_embedding_service.py
import logging
import time
from typing import List, Dict, Any, Tuple, Optional # Ensure Optional is imported

# Import services that fetch raw data
from services.one_piece_api_service import OnePieceAPIService
from controllers.news_controller import NewsController
from controllers.aniwatch_controller import AniwatchController
from services.anime_api_service import AnimeAPIService # Ensure this is correctly imported

logger = logging.getLogger(__name__)

class DataEmbeddingService:
    """
    Handles the process of fetching data from various sources,
    transforming it into suitable text format, and embedding it
    into the vector store.
    """

    def __init__(self, vector_store, embedder, anime_api_service: AnimeAPIService): # Make sure anime_api_service is expected here
        self.vector_store = vector_store
        self.embedder = embedder
        self.one_piece_api_service = OnePieceAPIService()
        self.news_controller = NewsController()
        self.aniwatch_controller = AniwatchController()
        self.anime_api_service = anime_api_service # This line is critical: ensure the passed service is assigned
        logger.debug("DataEmbeddingService: Initialized.")

    def embed_text_data(self, content: str, metadata: Dict[str, Any], source_item_id: Optional[str] = None):
        """Embeds a single piece of text content with its metadata."""
        try:
            # Check for existing document by source_item_id if p...
            # Ensure content is a string
            if not isinstance(content, str):
                content = str(content) # Convert to string if it's not already

            # Check if an item with this source_item_id already exists
            if source_item_id:
                existing_doc = self.vector_store.get_document_by_source_id(source_item_id)
                if existing_doc:
                    # Optionally, you could compare content/metadata and update if changed
                    # For now, we'll just skip re-embedding if it exists
                    logger.debug(f"Skipping embedding for existing document: {source_item_id}")
                    return True # Indicate successful processing (skipped)

            embedding = self.embedder.embed_text(content)
            if embedding:
                self.vector_store.add_document(content, embedding, metadata, source_item_id)
                return True
            else:
                logger.warning(f"Failed to generate embedding for content (first 50 chars): '{content[:50]}'")
                return False
        except Exception as e:
            logger.error(f"Error embedding data: {e}", exc_info=True)
            return False

    def embed_one_piece_data(self):
        logger.info("DataEmbeddingService: Starting One Piece data embedding...")
        processed_count = 0
        failed_count = 0
        try:
            # Fetch all characters - CORRECTED METHOD NAME
            characters_data, status_code = self.one_piece_api_service.get_characters()
            if status_code == 200 and characters_data:
                for char in characters_data:
                    character_id = char.get('id')
                    character_name = char.get('name')
                    description = char.get('description', '')
                    if character_name and character_id and description:
                        content = f"Character: {character_name}. Description: {description}"
                        metadata = {
                            "source": "One Piece API",
                            "type": "character",
                            "name": character_name,
                            "op_id": character_id
                        }
                        if self.embed_text_data(content, metadata, f"one_piece_char_{character_id}"):
                            processed_count += 1
                        else:
                            failed_count += 1
                    else:
                        logger.warning(f"Skipping One Piece character due to missing data: {char.get('name')} (ID: {char.get('id')})")
                        failed_count += 1
            else:
                logger.error(f"Failed to fetch One Piece characters: Status {status_code}, Data: {characters_data}")
                # If API call fails, consider all potential items as failed for reporting
                failed_count += (len(characters_data) if characters_data else 0)

            # Fetch all devil fruits - CORRECTED METHOD NAME
            devil_fruits_data, status_code = self.one_piece_api_service.get_devil_fruits()
            if status_code == 200 and devil_fruits_data:
                for df in devil_fruits_data:
                    df_id = df.get('id')
                    df_name = df.get('name')
                    description = df.get('description', '')
                    ability = df.get('ability', '')
                    if df_name and df_id and (description or ability):
                        content = f"Devil Fruit: {df_name}. Description: {description}. Ability: {ability}"
                        metadata = {
                            "source": "One Piece API",
                            "type": "devil_fruit",
                            "name": df_name,
                            "op_id": df_id
                        }
                        if self.embed_text_data(content, metadata, f"one_piece_df_{df_id}"):
                            processed_count += 1
                        else:
                            failed_count += 1
                    else:
                        logger.warning(f"Skipping One Piece Devil Fruit due to missing data: {df.get('name')} (ID: {df.get('id')})")
                        failed_count += 1
            else:
                logger.error(f"Failed to fetch One Piece devil fruits: Status {status_code}, Data: {devil_fruits_data}")
                failed_count += (len(devil_fruits_data) if devil_fruits_data else 0)

            # Fetch all crews - CORRECTED METHOD NAME
            crews_data, status_code = self.one_piece_api_service.get_crews()
            if status_code == 200 and crews_data:
                for crew in crews_data:
                    crew_id = crew.get('id')
                    crew_name = crew.get('name')
                    description = crew.get('description', '')
                    if crew_name and crew_id and description:
                        content = f"Crew: {crew_name}. Description: {description}"
                        metadata = {
                            "source": "One Piece API",
                            "type": "crew",
                            "name": crew_name,
                            "op_id": crew_id
                        }
                        if self.embed_text_data(content, metadata, f"one_piece_crew_{crew_id}"):
                            processed_count += 1
                        else:
                            failed_count += 1
                    else:
                        logger.warning(f"Skipping One Piece crew due to missing data: {crew.get('name')} (ID: {crew.get('id')})")
                        failed_count += 1
            else:
                logger.error(f"Failed to fetch One Piece crews: Status {status_code}, Data: {crews_data}")
                failed_count += (len(crews_data) if crews_data else 0)

            # Fetch all islands - CORRECTED METHOD NAME
            islands_data, status_code = self.one_piece_api_service.get_islands()
            if status_code == 200 and islands_data:
                for island in islands_data:
                    island_id = island.get('id')
                    island_name = island.get('name')
                    description = island.get('description', '')
                    if island_name and island_id and description:
                        content = f"Island: {island_name}. Description: {description}"
                        metadata = {
                            "source": "One Piece API",
                            "type": "island",
                            "name": island_name,
                            "op_id": island_id
                        }
                        if self.embed_text_data(content, metadata, f"one_piece_island_{island_id}"):
                            processed_count += 1
                        else:
                            failed_count += 1
                    else:
                        logger.warning(f"Skipping One Piece island due to missing data: {island.get('name')} (ID: {island.get('id')})")
                        failed_count += 1
            else:
                logger.error(f"Failed to fetch One Piece islands: Status {status_code}, Data: {islands_data}")
                failed_count += (len(islands_data) if islands_data else 0)

        except Exception as e:
            logger.error(f"DataEmbeddingService: Error during One Piece data embedding: {e}", exc_info=True)
            # Cannot determine exact count if a broad error occurs, log and reset
            processed_count = 0
            failed_count = 0
        finally:
            logger.info(f"DataEmbeddingService: Finished One Piece data embedding. Processed {processed_count} items, Failed: {failed_count}.")

    def embed_ann_details_data(self, limit: int = 100):
        """
        Fetches recent ANN encyclopedia articles (reports) and embeds their details.
        """
        logger.info(f"DataEmbeddingService: Starting ANN data embedding with limit={limit}...")
        processed_total = 0
        failed_total = 0
        try:
            # CORRECTED: Call the right method and expect a list of dictionaries
            ann_articles, status_code = self.news_controller.get_recent_news_articles(limit=limit)

            if status_code == 200 and isinstance(ann_articles, list) and ann_articles:
                for article in ann_articles:
                    item_id = article.get('id')
                    item_type = article.get('type', 'news_item') # Default type

                    # Make content generation more robust for ANN items
                    content = article.get('title', '') # Primary source of text
                    if not content: # Fallback if 'title' is empty
                        content = f"{article.get('type', 'Item')} (ID: {item_id or 'N/A'})"
                        if article.get('name'): # Use 'name' if 'title' is empty and 'name' exists
                             content = article.get('name')
                        if article.get('vintage'):
                            content += f" from {article['vintage']}"

                    if content and item_id is not None: # Ensure content is not empty and ID exists
                        metadata = {
                            "source": "ANN News",
                            "ann_id": item_id,
                            "type": item_type,
                            "title": article.get('title'),
                            "url": article.get('url'),
                            "release_date": article.get('date'),
                            "creator": article.get('creator'),
                            "thumbnail": article.get('thumbnail')
                        }
                        if self.embed_text_data(content, metadata, f"ann_{item_id}"):
                            processed_total += 1
                        else:
                            failed_total += 1
                    else:
                        logger.warning(f"DataEmbeddingService: Skipping ANN item due to missing content or ID: {article.get('title', 'N/A')} (ID: {item_id})")
                        failed_total += 1
            elif status_code != 200:
                logger.error(f"DataEmbeddingService: Failed to fetch ANN news articles. Status: {status_code}, Error: {ann_articles.get('error', 'Unknown error')}")
                failed_total += limit # Account for all potential failures if API call itself failed
            else:
                logger.info("DataEmbeddingService: No ANN news articles returned or data format incorrect.")
        except Exception as e:
            logger.error(f"DataEmbeddingService: Error during ANN data embedding: {e}", exc_info=True)
            failed_total += limit # Assume all failed if a general exception occurs
        finally:
            logger.info(f"DataEmbeddingService: Finished ANN data embedding. Processed {processed_total} items, Failed: {failed_total}.")

    def embed_aniwatch_data(self, limit: int = 100, page_limit: int = 5):
        """
        Fetches recent Aniwatch (streaming site) data and embeds it.
        This focuses on popular recent anime from Aniwatch.
        """
        logger.info(f"DataEmbeddingService: Starting Aniwatch data embedding with limit={limit}, page_limit={page_limit}...")
        processed_total = 0
        failed_total = 0
        try:
            # AniwatchController.get_recent_episodes returns a tuple (data, status_code)
            # data is expected to be a list of episode dictionaries
            recent_episodes_data, status_code = self.aniwatch_controller.get_recent_episodes(limit=limit, page_limit=page_limit)

            if status_code == 200 and isinstance(recent_episodes_data, list) and recent_episodes_data:
                for episode in recent_episodes_data:
                    anime_id = episode.get('animeId')
                    episode_number = episode.get('episodeNum')
                    title = episode.get('animeTitle', 'No Title')
                    type_ = episode.get('type', 'Episode')

                    content = f"{type_}: {title} Episode {episode_number}. {episode.get('synopsis', '')}"
                    source_item_id = f"aniwatch_episode_{anime_id}_{episode_number}"

                    if content and anime_id and episode_number:
                        metadata = {
                            "source": "Aniwatch",
                            "type": type_,
                            "aniwatch_anime_id": anime_id,
                            "episode_number": episode_number,
                            "title": title,
                            "release_date": episode.get('releasedDate')
                        }
                        if self.embed_text_data(content, metadata, source_item_id):
                            processed_total += 1
                        else:
                            failed_total += 1
                    else:
                        logger.warning(f"DataEmbeddingService: Skipping Aniwatch episode due to missing content or ID: {title} (ID: {anime_id})")
                        failed_total += 1
            elif status_code != 200:
                logger.error(f"DataEmbeddingService: Failed to fetch Aniwatch data. Status: {status_code}, Error: {recent_episodes_data.get('error', 'Unknown error')}")
                failed_total += (limit * page_limit) # Account for all potential failures if API call itself failed
            else:
                logger.info("DataEmbeddingService: No Aniwatch data returned or data format incorrect.")
        except Exception as e:
            logger.error(f"DataEmbeddingService: Error during Aniwatch data embedding: {e}", exc_info=True)
            failed_total += (limit * page_limit) # Assume all failed if a general exception occurs
        finally:
            logger.info(f"DataEmbeddingService: Finished Aniwatch data embedding. Processed {processed_total} items, Failed: {failed_total}.")


    def embed_anime_api_data(self, limit: int = 100):
        """
        Fetches and embeds general anime data (top ten, top search, spotlights, trending)
        from the new Node.js anime-api.
        """
        logger.info(f"DataEmbeddingService: Starting Anime API general data embedding with limit={limit}...")
        processed_total = 0
        failed_total = 0
        try:
            # Home page data (spotlights, trending)
            home_data, status_code = self.anime_api_service.get_home_info()
            if status_code == 200 and home_data and home_data.get('success') and 'results' in home_data:
                # Iterate through expected lists within 'results'
                for section_name in ['spotlights', 'trending', 'topAiring', 'mostPopular', 'mostFavorite', 'latestCompleted', 'latestEpisode']:
                    for item in home_data['results'].get(section_name, []):
                        anime_id = item.get('id')
                        title = item.get('title')
                        synopsis = item.get('description', '') # Use 'description' from API response as synopsis

                        content = f"Anime ({section_name}): {title}. Synopsis: {synopsis}"
                        if content and anime_id:
                            metadata = {
                                "source": "Anime API",
                                "type": f"home_page_anime_{section_name}",
                                "anime_id": anime_id,
                                "title": title,
                                "section": section_name
                            }
                            if self.embed_text_data(content, metadata, f"anime_api_home_{section_name}_{anime_id}"):
                                processed_total += 1
                            else:
                                failed_total += 1
                        else:
                            logger.warning(f"DataEmbeddingService: Skipping Anime API home item ({section_name}) due to missing content or ID: {title} (ID: {anime_id})")
                            failed_total += 1
            else:
                logger.error(f"DataEmbeddingService: Failed to fetch Anime API home data: Status {status_code}, Data: {home_data}")
                failed_total += limit # Estimate failure count

            # Top Ten Anime
            top_ten_data, status_code = self.anime_api_service.get_top_ten_anime()
            if status_code == 200 and top_ten_data and top_ten_data.get('success') and 'results' in top_ten_data and 'topTen' in top_ten_data['results']:
                # Top Ten has nested 'today', 'week', 'month' lists
                for period in ['today', 'week', 'month']:
                    for item in top_ten_data['results']['topTen'].get(period, []):
                        anime_id = item.get('id')
                        title = item.get('name') # Top Ten uses 'name' instead of 'title'
                        # No direct synopsis in Top Ten items, use name/type
                        content = f"Top 10 Anime ({period}): {title} (Type: {item.get('showType', 'N/A')})"
                        if content and anime_id:
                            metadata = {
                                "source": "Anime API",
                                "type": f"top_ten_anime_{period}",
                                "anime_id": anime_id,
                                "title": title,
                                "period": period
                            }
                            if self.embed_text_data(content, metadata, f"anime_api_topten_{period}_{anime_id}"):
                                processed_total += 1
                            else:
                                failed_total += 1
                        else:
                            logger.warning(f"DataEmbeddingService: Skipping Anime API top ten item ({period}) due to missing content or ID: {title} (ID: {anime_id})")
                            failed_total += 1
            else:
                logger.error(f"DataEmbeddingService: Failed to fetch Anime API top ten data: Status {status_code}, Data: {top_ten_data}")
                failed_total += limit # Estimate failure count

            # Top Search Anime
            top_search_data, status_code = self.anime_api_service.get_top_search_anime(limit=limit)
            if status_code == 200 and top_search_data and top_search_data.get('success') and 'results' in top_search_data:
                for item in top_search_data['results']: # 'results' is directly a list of items here
                    anime_id = item.get('id')
                    title = item.get('title')
                    synopsis = item.get('description', '') # Use 'description' from API response as synopsis
                    content = f"Top Search Anime: {title}. Synopsis: {synopsis}"
                    if content and anime_id:
                        metadata = {
                            "source": "Anime API",
                            "type": "top_search_anime",
                            "anime_id": anime_id,
                            "title": title
                        }
                        if self.embed_text_data(content, metadata, f"anime_api_topsearch_{anime_id}"):
                            processed_total += 1
                        else:
                            failed_total += 1
                    else:
                        logger.warning(f"DataEmbeddingService: Skipping Anime API top search item due to missing content or ID: {title} (ID: {anime_id})")
                        failed_total += 1
            else:
                logger.error(f"DataEmbeddingService: Failed to fetch Anime API top search data: Status {status_code}, Data: {top_search_data}")
                failed_total += limit # Estimate failure count

        except Exception as e:
            logger.error(f"DataEmbeddingService: Error during Anime API general data embedding: {e}", exc_info=True)
            processed_total = 0 # Reset counts on broad error
            failed_total = 0
        finally:
            logger.info(f"DataEmbeddingService: Finished Anime API general data embedding. Processed {processed_total} items, Failed: {failed_total}.")


    def embed_anime_api_category_data(self, categories: List[str], limit_per_category: int = 50):
        """
        Fetches and embeds anime data for specific categories from the Node.js anime-api.
        """
        logger.info(f"DataEmbeddingService: Starting Anime API category data embedding for categories: {categories} with limit_per_category={limit_per_category}...")
        processed_total = 0
        failed_total = 0

        for category in categories:
            logger.debug(f"DataEmbeddingService: Fetching data for category: {category}")
            try:
                # Assuming get_anime_by_category returns a dictionary with 'results' key
                category_data, status_code = self.anime_api_service.get_anime_by_category(category, limit=limit_per_category)

                if status_code == 200 and category_data and category_data.get('success') and 'results' in category_data:
                    # CORRECTED: Iterate over 'data' list within 'results'
                    for item in category_data['results'].get('data', []):
                        anime_id = item.get('id')
                        title = item.get('title')
                        synopsis = item.get('description', '') # Use 'description' from API response as synopsis

                        content = f"Anime in category '{category}': {title}. Synopsis: {synopsis}"
                        if content and anime_id:
                            metadata = {
                                "source": "Anime API",
                                "type": "category_anime",
                                "anime_id": anime_id,
                                "title": title,
                                "category": category
                            }
                            if self.embed_text_data(content, metadata, f"anime_api_category_{category}_{anime_id}"):
                                processed_total += 1
                            else:
                                failed_total += 1
                        else:
                            logger.warning(f"DataEmbeddingService: Skipping Anime API category item due to missing content or ID: {title} (ID: {anime_id})")
                            failed_total += 1
                elif status_code != 200:
                    logger.error(f"DataEmbeddingService: Failed to fetch Anime API category '{category}' data. Status: {status_code}, Error: {category_data.get('error', 'Unknown error')}")
                    failed_total += limit_per_category # Estimate failures
                else:
                    logger.info(f"DataEmbeddingService: No data returned for Anime API category: {category}")
            except Exception as e:
                logger.error(f"DataEmbeddingService: Error fetching/embedding data for category '{category}': {e}", exc_info=True)
                failed_total += limit_per_category # Estimate failures

        logger.info(f"DataEmbeddingService: Finished Anime API category data embedding. Processed {processed_total}, Failed: {failed_total}.")
        return processed_total, failed_total


    def embed_all_data(self):
        """Orchestrates the embedding of data from all configured sources."""
        logger.debug("DataEmbeddingService: Starting embedding of all data...")

        # VectorStore's load method handles persistence, new data will be appended
        logger.info("VectorStore: Existing documents retained. Appending new data.")

        self.embed_one_piece_data()
        # This now calls the correctly named method and handles its output
        self.embed_ann_details_data(limit=100)
        # Ignoring Aniwatch as per your instruction
        # self.embed_aniwatch_data(limit=100, page_limit=5)
        self.embed_anime_api_data(limit=100)

        common_categories = [\
            "top-airing", "most-popular", "completed", "movie", "tv",
            "genre/action", "genre/comedy", "producer/ufotable", "genre/fantasy", "genre/adventure",
            "genre/sci-fi", "genre/drama", "genre/slice-of-life", "genre/thriller",
            "genre/supernatural", "genre/romance", "genre/mystery"
        ]
        self.embed_anime_api_category_data(categories=common_categories, limit_per_category=50)

        # After embedding, save the updated vector store
        self.vector_store.save()
        logger.info("DataEmbeddingService: All data embedding complete. Vector store saved.")
