# backend/services/anime_api_service.py
import requests
import logging
import json

logger = logging.getLogger(__name__)

ANIME_API_BASE_URL = "http://localhost:4444"

class AnimeAPIService:
    def __init__(self):
        self.base_url = ANIME_API_BASE_URL
        logger.info(f"AnimeAPIService: Initialized with base URL: {self.base_url}")

    def _make_request(self, endpoint: str, params: dict = None) -> tuple[dict, int]:
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"AnimeAPIService: Making request to: {url} with params: {params}")
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            if response.status_code != 200:
                logger.error(f"AnimeAPIService: API Error {response.status_code} from {url}: {response.text}")
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError as e:
            logger.error(f"AnimeAPIService: Connection error to {url}: {e}")
            return {"error": f"Connection error: {e}"}, 503
        except requests.exceptions.Timeout:
            logger.error(f"AnimeAPIService: Request to {url} timed out.")
            return {"error": "Request timed out"}, 408
        except requests.exceptions.RequestException as e:
            logger.error(f"AnimeAPIService: Request error to {url}: {e}")
            return {"error": f"Request error: {e}"}, 500
        except json.JSONDecodeError:
            logger.error(f"AnimeAPIService: Failed to decode JSON response from {url}: {response.text}")
            return {"error": "Invalid JSON response"}, 500
        except Exception as e:
            logger.error(f"AnimeAPIService: An unexpected error occurred for {url}: {e}", exc_info=True)
            return {"error": f"An unexpected error occurred: {e}"}, 500

    def get_home_info(self) -> tuple[dict, int]:
        logger.info("AnimeAPIService: Fetching home info.")
        return self._make_request("/api/")

    def get_top_ten_anime(self) -> tuple[dict, int]:
        logger.info("AnimeAPIService: Fetching top ten anime.")
        return self._make_request("/api/top-ten")

    def get_top_search_anime(self, limit: int = 20) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching top search anime with limit: {limit}")
        params = {"limit": limit}
        return self._make_request("/api/top-search", params=params)

    def search_anime(self, query: str, page: int = 1) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Searching anime for query: '{query}', page: {page}")
        params = {"keyword": query, "page": page}
        return self._make_request("/api/search", params=params)

    # --- START OF FIX: Add the missing function ---
    def get_estimated_schedules(self, date: str) -> tuple[dict, int]:
        """
        Fetches estimated schedules for anime from the API.
        Corresponds to /api/schedule?date={date} in the Node.js API.
        """
        logger.info(f"AnimeAPIService: Fetching estimated schedules for date: '{date}'")
        endpoint = "/api/schedule"
        params = {"date": date}
        return self._make_request(endpoint, params)
    # --- END OF FIX ---

    def get_search_suggestions(self, keyword: str) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching search suggestions for keyword: '{keyword}'")
        params = {"keyword": keyword}
        return self._make_request("/api/search/suggest", params=params)

    def get_anime_info(self, anime_id: str) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching comprehensive info for anime ID: {anime_id} using /api/info.")
        params = {"id": anime_id}
        return self._make_request("/api/info", params=params)

    def get_anime_by_category(self, category: str, page: int = 1, limit: int = 20) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching anime for category: {category}, page: {page}, limit: {limit}")
        params = {"page": page, "limit": limit}
        return self._make_request(f"/api/{category}", params=params)

    def get_episode_list(self, anime_id: str) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching episode list for anime ID: {anime_id}")
        return self._make_request(f"/api/episodes/{anime_id}")

    def get_available_servers(self, anime_id: str, episode_id: str = None) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching available servers for anime ID: {anime_id}, episode ID: {episode_id}")
        params = {}
        if episode_id:
            params['ep'] = episode_id
        return self._make_request(f"/api/servers/{anime_id}", params=params)

    def get_streaming_info(self, episode_id: str, server: str, stream_type: str = "sub") -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching streaming info for episode ID: {episode_id}, server: {server}, type: {stream_type}")
        endpoint = "/api/stream"
        params = {"id": episode_id, "server": server, "type": stream_type}
        return self._make_request(endpoint, params=params)

    def get_characters_list(self, anime_id: str, page: int = 1) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching characters list for anime ID: {anime_id}, page: {page}")
        params = {"page": page}
        return self._make_request(f"/api/character/list/{anime_id}")

    def get_related_anime(self, anime_id: str) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching related anime for anime ID: {anime_id}")
        return self._make_request(f"/api/related/{anime_id}")

    def get_recommended_anime(self, anime_id: str) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching recommended anime for anime ID: {anime_id}")
        return self._make_request(f"/api/recommendations/{anime_id}")

    def get_character_details(self, character_id: str) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching details for character ID: {character_id}")
        return self._make_request(f"/api/character/{character_id}")

    def get_voice_actor_details(self, actor_id: str) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching details for voice actor ID: {actor_id}")
        return self._make_request(f"/api/actors/{actor_id}")

    def get_qtip_info(self, qtip_id: int) -> tuple[dict, int]:
        logger.info(f"AnimeAPIService: Fetching Qtip info for ID: {qtip_id}")
        return self._make_request(f"/api/qtip/{qtip_id}")
