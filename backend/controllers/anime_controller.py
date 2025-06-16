# backend/controllers/anime_controller.py
from flask import Blueprint, jsonify, request
from services.anime_api_service import AnimeAPIService
import logging
import re # Import regex for parsing data_id from episode id

logger = logging.getLogger(__name__)

class AnimeController:
    """
    Controller for handling data from the new 'anime-api' Node.js project.
    It calls the AnimeAPIService to fetch raw data and then formats it for the Flask API response.
    """
    def __init__(self):
        self.anime_api_service = AnimeAPIService()
        logger.info("AnimeController: Initialized.")

    def _ensure_is_list(self, value):
        """Helper to ensure a value is a list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            # If it's a string, wrap it in a list
            return [value]
        # For None or other types, return an empty list
        return []

    def _format_search_results(self, anime_list: list) -> list:
        """Helper to format the specific structure from the /api/search endpoint."""
        formatted = []
        if not isinstance(anime_list, list):
            logger.warning(f"Search result data for formatting is not a list: {type(anime_list)}")
            return []

        for anime in anime_list:
            # The search result items are dictionaries themselves
            if not isinstance(anime, dict) or not anime.get("id"):
                continue
            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "jname": anime.get("japanese_title"),
                "show_type": anime.get("showType"),
                "score": None # The /search endpoint doesn't seem to provide a score
            })
        return formatted

    def get_home_page_data(self) -> tuple[dict, int]:
        """
        Fetches and formats home page data from the 'anime-api'.
        """
        logger.debug("AnimeController: Fetching home page data.")
        raw_data, status_code = self.anime_api_service.get_home_info()

        if status_code != 200:
            return raw_data, status_code # Propagate error from service

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error("AnimeController: Invalid or missing 'results' in home page data.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']

        formatted_home_data = {
            "spotlights": self._format_anime_list_home(results.get("spotlights", [])),
            "trending": self._format_anime_list_home(results.get("trending", [])),
            "today_schedule": self._format_anime_list_home(results.get("today_schedule", [])),
            "top_airing": self._format_anime_list_home(results.get("top_airing", [])),
            "most_popular": self._format_anime_list_home(results.get("most_popular", [])),
            "most_favorite": self._format_anime_list_home(results.get("most_favorite", [])),
            "latest_completed": self._format_anime_list_home(results.get("latest_completed", [])),
            "latest_episode": self._format_anime_list_home(results.get("latest_episode", [])),
            "genres": results.get("genres", [])
        }
        return formatted_home_data, 200

    def get_top_ten_anime_data(self) -> tuple[dict, int]:
        """
        Fetches and formats top 10 anime data.
        """
        logger.debug("AnimeController: Fetching top ten anime data.")
        raw_data, status_code = self.anime_api_service.get_top_ten_anime()
        if status_code != 200:
            return raw_data, status_code
        # The structure for top-ten is nested under results -> topTen
        results_dict = raw_data.get("results", {}).get("topTen", {})
        return {
            "today": self._format_anime_list_common(results_dict.get("today", [])),
            "week": self._format_anime_list_common(results_dict.get("week", [])),
            "month": self._format_anime_list_common(results_dict.get("month", []))
        }, 200

    def search_anime_data(self, query: str, page: int = 1) -> tuple[dict, int]:
        """
        Searches for anime based on a query and formats the results.
        """
        logger.debug(f"AnimeController: Searching anime for query: {query}, page: {page}")
        raw_data, status_code = self.anime_api_service.search_anime(query, page)
        if status_code != 200:
            return raw_data, status_code

        results_dict = raw_data.get("results", {})
        anime_list = results_dict.get("data", []) if isinstance(results_dict, dict) else []
        total_pages = results_dict.get("totalPages", 1) if isinstance(results_dict, dict) else 1

        formatted_results = {
            "results": self._format_search_results(anime_list),
            "totalPages": total_pages
        }

        return formatted_results, 200


    def get_anime_by_category_data(self, category: str, page: int = 1) -> tuple[dict, int]:
        """
        Fetches and formats anime by category.
        """
        logger.debug(f"AnimeController: Fetching anime by category: {category}, page: {page}")
        raw_data, status_code = self.anime_api_service.get_anime_by_category(category, page)
        if status_code != 200:
            return raw_data, status_code

        results_dict = raw_data.get("results", {})
        anime_list = results_dict.get("data", []) if isinstance(results_dict, dict) else []
        total_pages = results_dict.get("totalPages", 1) if isinstance(results_dict, dict) else 1

        formatted_results = {
            "data": self._format_anime_list_common(anime_list),
            "totalPages": total_pages
        }

        return formatted_results, 200

    def get_anime_details_data(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches comprehensive details for a specific anime and formats them.
        """
        logger.debug(f"AnimeController: Fetching comprehensive details for anime ID: {anime_id}")

        main_info_data, main_info_status = self.anime_api_service.get_anime_info(anime_id)
        if main_info_status != 200 or not main_info_data.get('success'):
            logger.error(f"AnimeController: Failed to fetch main info for {anime_id}. Status: {main_info_status}, Data: {main_info_data}")
            return {"error": f"Failed to retrieve main anime details: {main_info_data.get('message', 'Unknown error')}"}, main_info_status

        results = main_info_data.get('results', {})
        anime_data = results.get('data', {})
        anime_info_nested = anime_data.get('animeInfo', {})

        if not anime_data:
            logger.error(f"AnimeController: No 'data' found in results for main info of {anime_id}.")
            return {"error": "No anime details found for the given ID."}, 404

        formatted_details = {
            "id": anime_data.get("id"),
            "data_id": anime_data.get("data_id"),
            "title": anime_data.get("title"),
            "japanese_title": anime_data.get("japanese_title"),
            "synonyms": self._ensure_is_list(anime_info_nested.get("Synonyms")),
            "poster_url": anime_data.get("poster"),
            "trailer_url": anime_data.get("trailer"),
            "synopsis": anime_info_nested.get("Overview"),
            "show_type": anime_data.get("showType"),
            "status": anime_info_nested.get("Status"),
            "aired": anime_info_nested.get("Aired"),
            "premiered": anime_info_nested.get("Premiered"),
            "broadcast": anime_data.get("broadcast"),
            "producers": self._ensure_is_list(anime_info_nested.get("Producers")),
            "licensors": self._ensure_is_list(anime_data.get("licensors")),
            "studios": self._ensure_is_list(anime_info_nested.get("Studios")),
            "source": anime_data.get("source"),
            "genres": self._ensure_is_list(anime_info_nested.get("Genres")),
            "duration": anime_info_nested.get("Duration"),
            "rating": anime_data.get("rating"),
            "mal_score": anime_info_nested.get("MAL Score"),
            "scored_by": anime_data.get("scored_by"),
            "rank": anime_data.get("rank"),
            "popularity": anime_data.get("popularity"),
            "members": anime_data.get("members"),
            "favorites": anime_data.get("favorites"),
            "total_episodes_count": anime_data.get("total_episodes"),
            "episodes": [],
            "characters_voice_actors": [],
            "seasons": self._format_seasons(results.get("seasons", [])),
            "related_anime": [],
            "recommended_anime": []
        }

        episodes_data, episodes_status = self.anime_api_service.get_episode_list(anime_id)
        # --- START FIX ---
        if episodes_status == 200 and episodes_data.get('success'):
            # The actual list is nested under 'results' -> 'episodes'
            episode_list = episodes_data.get("results", {}).get("episodes", [])
            formatted_details["episodes"] = self._format_episodes(episode_list)
        else:
            logger.warning(f"AnimeController: Failed to fetch episodes for {anime_id}. Status: {episodes_status}, Data: {episodes_data}")
        # --- END FIX ---

        characters_data, characters_status = self.anime_api_service.get_characters_list(anime_id)
        if characters_status == 200 and characters_data.get('success'):
            formatted_details["characters_voice_actors"] = self._format_characters_voice_actors(characters_data.get("results", []))
        else:
            logger.warning(f"AnimeController: Failed to fetch characters for {anime_id}. Status: {characters_status}, Data: {characters_data}")

        related_data, related_status = self.anime_api_service.get_related_anime(anime_id)
        if related_status == 200 and related_data.get('success'):
            formatted_details["related_anime"] = self._format_anime_list_common(related_data.get("results", []))
        else:
            logger.warning(f"AnimeController: Failed to fetch related anime for {anime_id}. Status: {related_status}, Data: {related_data}")

        recommended_data, recommended_status = self.anime_api_service.get_recommended_anime(anime_id)
        if recommended_status == 200 and recommended_data.get('success'):
            formatted_details["recommended_anime"] = self._format_anime_list_common(recommended_data.get("results", []))
        else:
            logger.warning(f"AnimeController: Failed to fetch recommended anime for {anime_id}. Status: {recommended_status}, Data: {recommended_data}")

        return formatted_details, 200

    def get_qtip_info_data(self, qtip_id: int) -> tuple[dict, int]:
        """
        Fetches and formats Qtip (quick info) data.
        """
        logger.debug(f"AnimeController: Fetching Qtip info for ID: {qtip_id}")
        raw_data, status_code = self.anime_api_service.get_qtip_info(qtip_id)
        if status_code != 200:
            return raw_data, status_code
        return raw_data.get("results", {}), 200

    def get_character_details_data(self, character_id: str) -> tuple[dict, int]:
        """
        Fetches and formats character details.
        """
        logger.debug(f"AnimeController: Fetching character details for ID: {character_id}")
        raw_data, status_code = self.anime_api_service.get_character_details(character_id)
        if status_code != 200:
            return raw_data, status_code
        return self._format_character_details(raw_data.get("results", {})), 200

    def get_voice_actor_details_data(self, actor_id: str) -> tuple[dict, int]:
        """
        Fetches and formats voice actor details.
        """
        logger.debug(f"AnimeController: Fetching voice actor details for ID: {actor_id}")
        raw_data, status_code = self.anime_api_service.get_voice_actor_details(actor_id)
        if status_code != 200:
            return raw_data, status_code
        return self._format_voice_actor_details(raw_data.get("results", {})), 200

    def get_available_servers_data(self, anime_id: str, episode_data_id: str) -> tuple[dict, int]:
        """
        Fetches and formats available servers for an anime episode.
        """
        logger.debug(f"AnimeController: Fetching servers for anime ID: {anime_id}, episode data_id: {episode_data_id}")
        raw_data, status_code = self.anime_api_service.get_available_servers(anime_id, episode_data_id)
        if status_code != 200:
            return raw_data, status_code
        return {"servers": self._format_servers(raw_data.get("results", []))}, 200

    def get_streaming_info_data(self, anime_id: str, server_id: str, stream_type: str) -> tuple[dict, int]:
        """
        Fetches and formats streaming information for a selected server and episode.
        """
        logger.debug(f"AnimeController: Fetching streaming info for anime ID: {anime_id}, server ID: {server_id}, type: {stream_type}")
        raw_data, status_code = self.anime_api_service.get_streaming_info(anime_id, server_id, stream_type)
        if status_code != 200:
            return raw_data, status_code
        return {"streaming_links": self._format_streaming_info(raw_data.get("results", {}))}, 200


    def _format_anime_list_home(self, anime_list: list) -> list:
        """Helper to format general anime list structures for home page."""
        formatted = []
        for anime in anime_list:
            if not anime.get("id"):
                continue
            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "jname": anime.get("jname"),
                "show_type": anime.get("type"),
                "score": anime.get("score")
            })
        return formatted

    def _format_anime_list_common(self, anime_list: list) -> list:
        """Helper to format common anime list structures (search, category, related, recommended)."""
        formatted = []
        if not isinstance(anime_list, list):
             logger.warning(f"Data for formatting is not a list: {type(anime_list)}")
             return []

        for anime in anime_list:
            if not isinstance(anime, dict) or not anime.get("id"):
                continue
            formatted.append({
                "id": anime.get("id"),
                "title": anime.get("title"),
                "poster_url": anime.get("poster"),
                "jname": anime.get("jname"),
                "show_type": anime.get("type"),
                "score": anime.get("score")
            })
        return formatted


    def _format_episodes(self, episodes_list: list) -> list:
        """
        Helper to format episodes list structures.
        """
        formatted = []
        if not isinstance(episodes_list, list):
            logger.error(f"Cannot format episodes, expected a list but got {type(episodes_list)}")
            return []

        for episode in episodes_list:
            # Add a check to ensure 'episode' is a dictionary
            if not isinstance(episode, dict):
                logger.warning(f"Skipping episode formatting because item is not a dictionary: {episode}")
                continue

            episode_id_from_node = episode.get("id")
            extracted_data_id = episode.get("data_id")

            if extracted_data_id is None and episode_id_from_node:
                match = re.search(r'\?ep=(\d+)', episode_id_from_node)
                if match:
                    extracted_data_id = match.group(1)
                    logger.info(f"Extracted data_id: {extracted_data_id} from episode ID: {episode_id_from_node}")
                else:
                    logger.warning(f"Could not extract data_id from episode ID: {episode_id_from_node}")

            formatted.append({
                "id": episode_id_from_node,
                "episode_no": episode.get("episode"),
                "data_id": extracted_data_id,
                "title": episode.get("title"),
                "japanese_title": episode.get("japanese_title")
            })
        return formatted

    def _format_seasons(self, seasons_list: list) -> list:
        """Helper to format seasons list structures."""
        formatted = []
        for season in seasons_list:
            formatted.append({
                "id": season.get("id"),
                "data_number": season.get("data_number"),
                "data_id": season.get("data_id"),
                "season_name": season.get("season"),
                "title": season.get("title"),
                "japanese_title": season.get("japanese_title"),
                "season_poster_url": season.get("season_poster")
            })
        return formatted

    def _format_characters_voice_actors(self, characters_data: list) -> list:
        """Helper to format characters and voice actors list structures."""
        formatted = []
        for char_info in characters_data:
            character = char_info.get("character", {})
            voice_actors = char_info.get("voiceActors", [])
            formatted_v_actors = []
            for va in voice_actors:
                formatted_v_actors.append({
                    "id": va.get("id"),
                    "name": va.get("name"),
                    "poster_url": va.get("poster")
                })
            formatted.append({
                "character_id": character.get("id"),
                "character_name": character.get("name"),
                "character_poster_url": character.get("poster"),
                "character_cast": character.get("cast"),
                "voice_actors": formatted_v_actors
            })
        return formatted

    def _format_character_details(self, character_data: dict) -> dict:
        """Helper to format single character details."""
        if not character_data:
            return {}
        return {
            "id": character_data.get("id"),
            "name": character_data.get("name"),
            "poster_url": character_data.get("poster"),
            "description": character_data.get("description"),
            "animeography": self._format_anime_list_common(character_data.get("animeography", [])),
            "mangaography": character_data.get("mangaography", []),
            "voice_actors": self._format_characters_voice_actors([{"voiceActors": character_data.get("voiceActors", [])}]).pop().get("voice_actors", [])
        }

    def _format_voice_actor_details(self, actor_data: dict) -> dict:
        """Helper to format single voice actor details."""
        if not actor_data:
            return {}
        return {
            "id": actor_data.get("id"),
            "name": actor_data.get("name"),
            "poster_url": actor_data.get("poster"),
            "description": actor_data.get("description"),
            "language": actor_data.get("language"),
            "characters_played": self._format_characters_voice_actors(actor_data.get("characters_played", []))
        }

    def _format_servers(self, servers_list: list) -> list:
        """Helper to format available servers list."""
        formatted = []
        for server in servers_list:
            formatted.append({
                "type": server.get("type"),
                "data_id": server.get("data_id"),
                "server_id": server.get("server_id"),
                "server_name": server.get("serverName")
            })
        return formatted

    def _format_streaming_info(self, streaming_info: dict) -> list:
        """Helper to format streaming info, specifically extracting links."""
        if not streaming_info:
            return []
        links = []
        streaming_link_details = streaming_info.get("streamingLink", {})
        file_link = streaming_link_details.get("link", {}).get("file")
        server_name = streaming_link_details.get("server")
        link_type = streaming_link_details.get("type")
        if file_link:
            links.append({
                "file": file_link,
                "server": server_name,
                "type": link_type
            })
        return links

anime_controller = AnimeController()
