# backend/controllers/anime_controller.py
from flask import Blueprint, jsonify, request
from services.anime_api_service import AnimeAPIService
import logging

logger = logging.getLogger(__name__)

class AnimeController:
    """
    Controller for handling data from the new 'anime-api' Node.js project.
    It calls the AnimeAPIService to fetch raw data and then formats it for the Flask API response.
    """
    def __init__(self):
        self.anime_api_service = AnimeAPIService()
        logger.info("AnimeController: Initialized.")

    def get_home_page_data(self) -> tuple[dict, int]:
        """
        Fetches and formats home page data from the 'anime-api'.
        """
        logger.debug("AnimeController: Fetching home page data.")
        raw_data, status_code = self.anime_api_service.get_home_info()

        if status_code != 200:
            return raw_data, status_code # Propagate error from service

        # Check if 'results' key exists and is not None
        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error("AnimeController: Invalid or missing 'results' in home page data.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']

        # Format the response based on the 'anime-api' schema
        formatted_home_data = {
            "spotlights": self._format_anime_list_home(results.get("spotlights", [])),
            "trending": self._format_anime_list_home(results.get("trending", [])),
            "today_schedule": self._format_schedule_list(results.get("today", {}).get("schedule", [])),
            "top_airing": self._format_anime_list_home(results.get("topAiring", [])),
            "most_popular": self._format_anime_list_home(results.get("mostPopular", [])),
            "most_favorite": self._format_anime_list_home(results.get("mostFavorite", [])),
            "latest_completed": self._format_anime_list_home(results.get("latestCompleted", [])),
            "latest_episode": self._format_anime_list_home(results.get("latestEpisode", [])),
            "genres": results.get("genres", []),
        }

        logger.debug("AnimeController: Successfully formatted home page data.")
        return formatted_home_data, 200

    def get_top_ten_anime_data(self) -> tuple[dict, int]:
        """
        Fetches and formats top 10 anime data from the 'anime-api'.
        """
        logger.debug("AnimeController: Fetching top ten anime data.")
        raw_data, status_code = self.anime_api_service.get_top_ten_info()

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data or 'topTen' not in raw_data['results']:
            logger.error("AnimeController: Invalid or missing 'results.topTen' in top ten data.")
            return {"error": "Invalid data format from external API."}, 500

        top_ten_results = raw_data['results']['topTen']
        formatted_top_ten_data = {
            "today": self._format_anime_list_top_ten(top_ten_results.get("today", [])),
            "week": self._format_anime_list_top_ten(top_ten_results.get("week", [])),
            "month": self._format_anime_list_top_ten(top_ten_results.get("month", [])),
        }
        logger.debug("AnimeController: Successfully formatted top ten anime data.")
        return formatted_top_ten_data, 200

    def get_top_search_data(self) -> tuple[dict, int]:
        """
        Fetches and formats top search data from the 'anime-api'.
        """
        logger.debug("AnimeController: Fetching top search data.")
        raw_data, status_code = self.anime_api_service.get_top_search_info()

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error("AnimeController: Invalid or missing 'results' in top search data.")
            return {"error": "Invalid data format from external API."}, 500

        formatted_results = [{
            "title": item.get("title"),
            "link": item.get("link")
        } for item in raw_data['results']]

        logger.debug("AnimeController: Successfully formatted top search data.")
        return {"results": formatted_results}, 200


    def get_anime_details(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches and formats details for a specific anime from the 'anime-api'.
        """
        logger.debug(f"AnimeController: Fetching details for anime ID: {anime_id}")
        raw_data, status_code = self.anime_api_service.get_anime_info(anime_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data or 'data' not in raw_data['results']:
            logger.error(f"AnimeController: Invalid or missing 'results.data' in anime details for ID {anime_id}.")
            return {"error": "Invalid data format from external API."}, 500

        anime_data = raw_data['results']['data']
        anime_info = anime_data.get("animeInfo", {})

        # Format related and recommended data
        related_data = []
        for group in raw_data['results'].get('related_data', []):
            related_data.extend(self._format_anime_list_general(group)) # Use general formatter

        recommended_data = []
        for group in raw_data['results'].get('recommended_data', []):
            recommended_data.extend(self._format_anime_list_general(group)) # Use general formatter


        formatted_details = {
            "id": anime_data.get("id"),
            "data_id": anime_data.get("data_id"),
            "title": anime_data.get("title"),
            "japanese_title": anime_data.get("japanese_title"),
            "poster_url": anime_data.get("poster"),
            "show_type": anime_data.get("showType"),
            "adult_content": anime_data.get("adultContent", False),
            "overview": anime_info.get("Overview"),
            "synonyms": anime_info.get("Synonyms"),
            "aired": anime_info.get("Aired"),
            "premiered": anime_info.get("Premiered"),
            "duration": anime_info.get("Duration"),
            "status": anime_info.get("Status"),
            "mal_score": anime_info.get("MAL Score"),
            "genres": anime_info.get("Genres", []),
            "studios": anime_info.get("Studios"),
            "producers": anime_info.get("Producers", []),
            "seasons": self._format_seasons_list(raw_data['results'].get('seasons', [])),
            "characters_voice_actors": self._format_characters_voice_actors(raw_data['results'].get('charactersVoiceActors', [])),
            "related_anime": related_data,
            "recommended_anime": recommended_data,
        }
        logger.debug(f"AnimeController: Successfully formatted details for anime ID {anime_id}.")
        return formatted_details, 200

    def get_random_anime_data(self) -> tuple[dict, int]:
        """
        Fetches and formats random anime data from the 'anime-api'.
        """
        logger.debug("AnimeController: Fetching random anime data.")
        raw_data, status_code = self.anime_api_service.get_random_anime_info()

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data or 'data' not in raw_data['results']:
            logger.error("AnimeController: Invalid or missing 'results.data' in random anime data.")
            return {"error": "Invalid data format from external API."}, 500

        anime_data = raw_data['results']['data']
        anime_info = anime_data.get("animeInfo", {})

        related_data = []
        for group in raw_data['results'].get('related_data', []):
            related_data.extend(self._format_anime_list_general(group))

        recommended_data = []
        for group in raw_data['results'].get('recommended_data', []):
            recommended_data.extend(self._format_anime_list_general(group))

        formatted_random_data = {
            "id": anime_data.get("id"),
            "data_id": anime_data.get("data_id"),
            "title": anime_data.get("title"),
            "japanese_title": anime_data.get("japanese_title"),
            "poster_url": anime_data.get("poster"),
            "show_type": anime_data.get("showType"),
            "adult_content": anime_data.get("adultContent", False),
            "overview": anime_info.get("Overview"),
            "synonyms": anime_info.get("Synonyms"),
            "aired": anime_info.get("Aired"),
            "premiered": anime_info.get("Premiered"),
            "duration": anime_info.get("Duration"),
            "status": anime_info.get("Status"),
            "mal_score": anime_info.get("MAL Score"),
            "genres": anime_info.get("Genres", []),
            "studios": anime_info.get("Studios"),
            "producers": anime_info.get("Producers", []),
            "seasons": self._format_seasons_list(raw_data['results'].get('seasons', [])),
            "characters_voice_actors": self._format_characters_voice_actors(raw_data['results'].get('charactersVoiceActors', [])),
            "related_anime": related_data,
            "recommended_anime": recommended_data,
        }
        logger.debug("AnimeController: Successfully formatted random anime data.")
        return formatted_random_data, 200

    def get_category_data(self, category: str, page: int = 1) -> tuple[dict, int]:
        """
        Fetches and formats anime list for a specific category from the 'anime-api'.
        """
        logger.debug(f"AnimeController: Fetching category '{category}' page {page}.")
        raw_data, status_code = self.anime_api_service.get_category_info(category, page)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in category '{category}' data.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']
        formatted_data = {
            "total_pages": results.get("totalPages"),
            "data": self._format_anime_list_category(results.get("data", []))
        }
        logger.debug(f"AnimeController: Successfully formatted category '{category}' data.")
        return formatted_data, 200

    def get_producer_studio_anime_data(self, producer: str, page: int = 1) -> tuple[dict, int]:
        """
        Fetches and formats anime list for a specific producer/studio from the 'anime-api'.
        """
        logger.debug(f"AnimeController: Fetching anime for producer/studio '{producer}' page {page}.")
        raw_data, status_code = self.anime_api_service.get_producer_studio_anime(producer, page)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in producer/studio '{producer}' data.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']
        formatted_data = {
            "total_pages": results.get("totalPages"),
            "data": self._format_anime_list_category(results.get("data", [])) # Re-use category formatter as structure is similar
        }
        logger.debug(f"AnimeController: Successfully formatted producer/studio '{producer}' data.")
        return formatted_data, 200

    def search_anime_data(self, keyword: str) -> tuple[dict, int]:
        """
        Searches and formats anime results by keyword from the 'anime-api'.
        """
        logger.debug(f"AnimeController: Searching anime for keyword: '{keyword}'.")
        raw_data, status_code = self.anime_api_service.search_anime_by_keyword(keyword)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in search data for keyword '{keyword}'.")
            return {"error": "Invalid data format from external API."}, 500

        formatted_results = self._format_anime_list_search(raw_data['results'])
        logger.debug(f"AnimeController: Successfully formatted search results for keyword '{keyword}'.")
        return {"results": formatted_results}, 200

    def get_anime_search_suggestions(self, keyword: str) -> tuple[dict, int]:
        """
        Fetches and formats search suggestions for a keyword from the 'anime-api'.
        """
        logger.debug(f"AnimeController: Fetching search suggestions for keyword: '{keyword}'.")
        raw_data, status_code = self.anime_api_service.get_search_suggestions(keyword)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in search suggestions for keyword '{keyword}'.")
            return {"error": "Invalid data format from external API."}, 500

        formatted_suggestions = self._format_anime_list_suggestion(raw_data['results'])
        logger.debug(f"AnimeController: Successfully formatted search suggestions for keyword '{keyword}'.")
        return {"suggestions": formatted_suggestions}, 200

    def filter_anime_data(self, params: dict) -> tuple[dict, int]:
        """
        Filters and formats anime data based on various criteria.
        """
        logger.debug(f"AnimeController: Filtering anime with params: {params}")
        raw_data, status_code = self.anime_api_service.filter_anime(params)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in filtered anime data for params: {params}.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']
        formatted_data = {
            "total_pages": results.get("totalPages"),
            "data": self._format_anime_list_category(results.get("data", [])) # Re-use category formatter
        }
        logger.debug(f"AnimeController: Successfully formatted filtered anime data with params: {params}.")
        return formatted_data, 200

    def get_anime_episode_list(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches and formats the episode list for a specific anime.
        """
        logger.debug(f"AnimeController: Fetching episode list for anime ID: {anime_id}")
        raw_data, status_code = self.anime_api_service.get_anime_episodes(anime_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in episode list for anime ID {anime_id}.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']
        formatted_episodes = {
            "total_episodes": results.get("totalEpisodes"),
            "episodes": [{
                "episode_no": ep.get("episode_no"),
                "id": ep.get("id"),
                "data_id": ep.get("data_id"),
                "jname": ep.get("jname"),
                "title": ep.get("title"),
                "japanese_title": ep.get("japanese_title")
            } for ep in results.get("episodes", [])]
        }
        logger.debug(f"AnimeController: Successfully formatted episode list for anime ID {anime_id}.")
        return formatted_episodes, 200

    def get_upcoming_schedule_data(self, date: str) -> tuple[dict, int]:
        """
        Fetches and formats the schedule of upcoming anime for a specific date.
        """
        logger.debug(f"AnimeController: Fetching upcoming schedule for date: {date}")
        raw_data, status_code = self.anime_api_service.get_upcoming_schedule(date)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in upcoming schedule for date {date}.")
            return {"error": "Invalid data format from external API."}, 500

        formatted_schedule = self._format_schedule_list(raw_data['results'])
        logger.debug(f"AnimeController: Successfully formatted upcoming schedule for date: {date}.")
        return {"results": formatted_schedule}, 200

    def get_next_episode_schedule_data(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches and formats the schedule of the next episode for a specific anime.
        """
        logger.debug(f"AnimeController: Fetching next episode schedule for anime ID: {anime_id}")
        raw_data, status_code = self.anime_api_service.get_next_episode_schedule(anime_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in next episode schedule for anime ID {anime_id}.")
            return {"error": "Invalid data format from external API."}, 500

        formatted_schedule = raw_data['results'].get("nextEpisodeSchedule")
        logger.debug(f"AnimeController: Successfully formatted next episode schedule for anime ID: {anime_id}.")
        return {"next_episode_schedule": formatted_schedule}, 200

    def get_characters_data(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches and formats the list of characters for a specific anime.
        """
        logger.debug(f"AnimeController: Fetching characters for anime ID: {anime_id}")
        raw_data, status_code = self.anime_api_service.get_characters_list(anime_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in characters list for anime ID {anime_id}.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']
        formatted_characters = {
            "current_page": results.get("currentPage"),
            "total_pages": results.get("totalPages"),
            "data": self._format_characters_voice_actors(results.get("data", []))
        }
        logger.debug(f"AnimeController: Successfully formatted characters list for anime ID {anime_id}.")
        return formatted_characters, 200

    def get_streaming_data(self, anime_id: str, server: str, stream_type: str) -> tuple[dict, int]:
        """
        Fetches and formats streaming information for an anime episode.
        """
        logger.debug(f"AnimeController: Fetching streaming info for ID: {anime_id}, server: {server}, type: {stream_type}")
        raw_data, status_code = self.anime_api_service.get_streaming_info(anime_id, server, stream_type)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in streaming data for ID: {anime_id}.")
            return {"error": "Invalid data format from external API."}, 500

        results = raw_data['results']
        # Defensive check: Ensure 'streamingLink' is a list before iterating
        streaming_links_raw = results.get("streamingLink", [])
        if streaming_links_raw is None: # Explicitly handle if it's None instead of a list
            streaming_links_raw = []

        formatted_streaming_links = []
        for link_data in streaming_links_raw: # Iterate over the potentially empty or corrected list
            formatted_streaming_links.append({
                "id": link_data.get("id"),
                "type": link_data.get("type"),
                "link": link_data.get("link"), # This is already structured correctly as {file, type}
                "tracks": link_data.get("tracks"),
                "intro": link_data.get("intro"),
                "outro": link_data.get("outro"),
                "server": link_data.get("server")
            })

        formatted_servers = []
        for server_data in results.get("servers", []):
            formatted_servers.append({
                "type": server_data.get("type"),
                "data_id": server_data.get("data_id"),
                "server_id": server_data.get("server_id"),
                "server_name": server_data.get("server_name")
            })

        formatted_data = {
            "streaming_links": formatted_streaming_links,
            "servers": formatted_servers
        }
        logger.debug(f"AnimeController: Successfully formatted streaming data for ID: {anime_id}.")
        return formatted_data, 200

    def get_available_servers_data(self, anime_id: str, episode_id: str = None) -> tuple[dict, int]:
        """
        Fetches and formats available servers for an anime episode.
        """
        logger.debug(f"AnimeController: Fetching available servers for anime ID: {anime_id}, episode ID: {episode_id}")
        raw_data, status_code = self.anime_api_service.get_available_servers(anime_id, episode_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in available servers for anime ID: {anime_id}.")
            return {"error": "Invalid data format from external API."}, 500

        formatted_servers = []
        for server_data in raw_data['results']:
            formatted_servers.append({
                "type": server_data.get("type"),
                "data_id": server_data.get("data_id"),
                "server_id": server_data.get("server_id"),
                "server_name": server_data.get("serverName") # Note: serverName here
            })
        logger.debug(f"AnimeController: Successfully formatted available servers for anime ID: {anime_id}.")
        return {"servers": formatted_servers}, 200

    def get_character_details_data(self, character_id: str) -> tuple[dict, int]:
        """
        Fetches and formats details for a specific character.
        """
        logger.debug(f"AnimeController: Fetching details for character ID: {character_id}")
        raw_data, status_code = self.anime_api_service.get_character_details(character_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data or not raw_data['results'].get('data'):
            logger.error(f"AnimeController: Invalid or missing 'results.data' in character details for ID {character_id}.")
            return {"error": "Invalid data format from external API."}, 500

        char_data = raw_data['results']['data'][0] # Assuming results.data is a list with one item
        formatted_details = {
            "id": char_data.get("id"),
            "name": char_data.get("name"),
            "profile_url": char_data.get("profile"),
            "japanese_name": char_data.get("japaneseName"),
            "about_description": char_data.get("about", {}).get("description"),
            "about_style": char_data.get("about", {}).get("style"),
            "voice_actors": [{
                "name": va.get("name"),
                "profile_url": va.get("profile"),
                "language": va.get("language"),
                "id": va.get("id")
            } for va in char_data.get("voiceActors", [])],
            "animeography": [{
                "title": ani.get("title"),
                "id": ani.get("id"),
                "role": ani.get("role"),
                "type": ani.get("type"),
                "poster_url": ani.get("poster")
            } for ani in char_data.get("animeography", [])]
        }
        logger.debug(f"AnimeController: Successfully formatted character details for ID {character_id}.")
        return formatted_details, 200

    def get_voice_actor_details_data(self, actor_id: str) -> tuple[dict, int]:
        """
        Fetches and formats details for a specific voice actor.
        """
        logger.debug(f"AnimeController: Fetching details for voice actor ID: {actor_id}")
        raw_data, status_code = self.anime_api_service.get_voice_actor_details(actor_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data or not raw_data['results'].get('data'):
            logger.error(f"AnimeController: Invalid or missing 'results.data' in voice actor details for ID {actor_id}.")
            return {"error": "Invalid data format from external API."}, 500

        actor_data = raw_data['results']['data'][0] # Assuming results.data is a list with one item
        formatted_details = {
            "id": actor_data.get("id"),
            "name": actor_data.get("name"),
            "profile_url": actor_data.get("profile"),
            "japanese_name": actor_data.get("japaneseName"),
            "about_description": actor_data.get("about", {}).get("description"),
            "about_style": actor_data.get("about", {}).get("style"),
            "roles": [{
                "anime": {
                    "title": role.get("anime", {}).get("title"),
                    "poster_url": role.get("anime", {}).get("poster"),
                    "type": role.get("anime", {}).get("type"),
                    "year": role.get("anime", {}).get("year"),
                    "id": role.get("anime", {}).get("id")
                },
                "character": {
                    "name": role.get("character", {}).get("name"),
                    "profile_url": role.get("character", {}).get("profile"),
                    "role": role.get("character", {}).get("role")
                }
            } for role in actor_data.get("roles", [])]
        }
        logger.debug(f"AnimeController: Successfully formatted voice actor details for ID {actor_id}.")
        return formatted_details, 200

    def get_qtip_data(self, qtip_id: int) -> tuple[dict, int]:
        """
        Fetches and formats Qtip information for a specific anime.
        """
        logger.debug(f"AnimeController: Fetching Qtip info for ID: {qtip_id}")
        raw_data, status_code = self.anime_api_service.get_qtip_info(qtip_id)

        if status_code != 200:
            return raw_data, status_code

        if not raw_data or not raw_data.get('success') or 'results' not in raw_data:
            logger.error(f"AnimeController: Invalid or missing 'results' in Qtip data for ID {qtip_id}.")
            return {"error": "Invalid data format from external API."}, 500

        qtip_results = raw_data['results']
        formatted_qtip = {
            "title": qtip_results.get("title"),
            "rating": qtip_results.get("rating"),
            "quality": qtip_results.get("quality"),
            "sub_count": qtip_results.get("subCount"),
            "dub_count": qtip_results.get("dubCount"),
            "episode_count": qtip_results.get("episodeCount"),
            "type": qtip_results.get("type"),
            "description": qtip_results.get("description"),
            "japanese_title": qtip_results.get("japaneseTitle"),
            "synonyms": qtip_results.get("Synonyms"),
            "aired_date": qtip_results.get("airedDate"),
            "status": qtip_results.get("status"),
            "genres": qtip_results.get("genres"),
            "watch_link": qtip_results.get("watchLink")
        }
        logger.debug(f"AnimeController: Successfully formatted Qtip data for ID: {qtip_id}.")
        return formatted_qtip, 200

    def _format_anime_list_home(self, anime_list: list) -> list:
        """Helper to format common anime list structures found in home endpoint."""
        formatted = []
        for anime in anime_list:
            tv_info = anime.get("tvInfo", {})
            formatted.append({
                "id": anime.get("id"),
                "data_id": anime.get("data_id"),
                "poster_url": anime.get("poster"),
                "title": anime.get("title"),
                "japanese_title": anime.get("japanese_title"),
                "description": anime.get("description"),
                "show_type": tv_info.get("showType"),
                "duration": tv_info.get("duration"),
                "release_date": tv_info.get("releaseDate"),
                "quality": tv_info.get("quality"),
                "sub_episodes": tv_info.get("sub"), # These are directly in tvInfo for home
                "dub_episodes": tv_info.get("dub"), # These are directly in tvInfo for home
                "total_episodes": tv_info.get("eps"),
                "number": anime.get("number"), # For trending
                "adult_content": anime.get("adultContent", False)
            })
        return formatted

    def _format_anime_list_general(self, anime_list: list) -> list:
        """Helper to format common anime list structures (e.g., related/recommended)."""
        formatted = []
        for anime in anime_list:
            tv_info = anime.get("tvInfo", {})
            formatted.append({
                "id": anime.get("id"),
                "data_id": anime.get("data_id"),
                "poster_url": anime.get("poster"),
                "title": anime.get("title"),
                "japanese_title": anime.get("japanese_title"),
                "description": anime.get("description"), # Might be empty
                "show_type": tv_info.get("showType"),
                "duration": tv_info.get("duration"),
                "sub_episodes": tv_info.get("sub"),
                "dub_episodes": tv_info.get("dub"),
                "total_episodes": tv_info.get("eps"),
                "adult_content": anime.get("adultContent", False)
            })
        return formatted

    def _format_anime_list_top_ten(self, anime_list: list) -> list:
        """Helper to format anime list structures for top-ten endpoint."""
        formatted = []
        for anime in anime_list:
            tv_info = anime.get("tvInfo", {})
            formatted.append({
                "id": anime.get("id"),
                "data_id": anime.get("data_id"),
                "number": anime.get("number"),
                "name": anime.get("name"), # 'name' here instead of 'title'
                "poster_url": anime.get("poster"),
                "show_type": tv_info.get("showType"),
                "duration": tv_info.get("duration"),
                "sub_episodes": tv_info.get("sub"),
                "dub_episodes": tv_info.get("dub"),
                "total_episodes": tv_info.get("eps")
            })
        return formatted

    def _format_anime_list_category(self, anime_list: list) -> list:
        """Helper to format anime list structures for category and producer endpoints."""
        formatted = []
        for anime in anime_list:
            tv_info = anime.get("tvInfo", {})
            formatted.append({
                "id": anime.get("id"),
                "data_id": anime.get("data_id"),
                "poster_url": anime.get("poster"),
                "title": anime.get("title"),
                "japanese_title": anime.get("japanese_title"),
                "description": anime.get("description"),
                "show_type": tv_info.get("showType"),
                "duration": tv_info.get("duration"),
                "sub_episodes": tv_info.get("sub"),
                "dub_episodes": tv_info.get("dub"),
                "total_episodes": tv_info.get("eps"),
                "adult_content": anime.get("adultContent", False)
            })
        return formatted

    def _format_anime_list_search(self, anime_list: list) -> list:
        """Helper to format anime list structures for search endpoint."""
        formatted = []
        for anime in anime_list:
            tv_info = anime.get("tvInfo", {})
            formatted.append({
                "id": anime.get("id"),
                "data_id": anime.get("data_id"),
                "poster_url": anime.get("poster"),
                "title": anime.get("title"),
                "japanese_title": anime.get("japanese_title"),
                "show_type": tv_info.get("showType"),
                "duration": tv_info.get("duration"),
                "sub_episodes": tv_info.get("sub"),
                "dub_episodes": tv_info.get("dub"),
                "total_episodes": tv_info.get("eps"),
            })
        return formatted

    def _format_anime_list_suggestion(self, anime_list: list) -> list:
        """Helper to format anime list structures for search suggestions endpoint."""
        formatted = []
        for anime in anime_list:
            formatted.append({
                "id": anime.get("id"),
                "data_id": anime.get("data_id"),
                "poster_url": anime.get("poster"),
                "title": anime.get("title"),
                "japanese_title": anime.get("japanese_title"),
                "release_date": anime.get("releaseDate"),
                "show_type": anime.get("showType"),
                "duration": anime.get("duration"),
            })
        return formatted


    def _format_schedule_list(self, schedule_list: list) -> list:
        """Helper to format schedule list structures."""
        formatted = []
        for item in schedule_list:
            formatted.append({
                "id": item.get("id"),
                "data_id": item.get("data_id"),
                "title": item.get("title"),
                "japanese_title": item.get("japanese_title"),
                "release_date": item.get("releaseDate"),
                "time": item.get("time"),
                "episode_no": item.get("episode_no")
            })
        return formatted

    def _format_seasons_list(self, seasons_list: list) -> list:
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

# Initialize the controller
anime_controller = AnimeController()

