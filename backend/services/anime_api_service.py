# backend/services/anime_api_service.py
import requests
import logging
import json # Import json for pretty printing in logs

logger = logging.getLogger(__name__)

# Define the base URL for your new local Node.js anime-api server
# Make sure this matches the port your Node.js server is listening on
ANIME_API_BASE_URL = "http://localhost:4444"

class AnimeAPIService:
    """
    Service for interacting with the local Node.js 'anime-api' (ThatGuyCalledAman/anime-api).
    Handles making HTTP requests to the Node.js API and returning raw JSON responses.
    """
    def __init__(self):
        self.base_url = ANIME_API_BASE_URL
        logger.info(f"AnimeAPIService: Initialized with base URL: {self.base_url}")

    def _make_request(self, endpoint: str, params: dict = None) -> tuple[dict, int]:
        """
        Helper method to make GET requests to the anime-api.

        Args:
            endpoint (str): The API endpoint (e.g., "/api/").
            params (dict, optional): Dictionary of query parameters. Defaults to None.

        Returns:
            tuple[dict, int]: A tuple containing the JSON response as a dictionary
                              and the HTTP status code.
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"AnimeAPIService: Making request to: {url} with params: {params}")
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

            # Log the full response content for debugging if an error occurs
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
        """
        Fetches home page information from the 'anime-api'.
        Corresponds to GET /api/.
        """
        logger.info("AnimeAPIService: Fetching home info.")
        return self._make_request("/api/")

    def get_top_ten_anime(self) -> tuple[dict, int]:
        """
        Fetches top 10 anime information.
        Corresponds to GET /api/top-ten.
        """
        logger.info("AnimeAPIService: Fetching top ten anime.")
        return self._make_request("/api/top-ten")

    def get_top_search_anime(self, limit: int = 20) -> tuple[dict, int]:
        """
        Fetches top search anime.
        Corresponds to GET /api/top-search?limit={limit}.
        """
        logger.info(f"AnimeAPIService: Fetching top search anime with limit: {limit}")
        params = {"limit": limit}
        return self._make_request("/api/top-search", params=params)

    def search_anime(self, query: str, page: int = 1) -> tuple[dict, int]:
        """
        Searches for anime by query.
        Corresponds to GET /api/search?q={query}&page={page}.
        """
        logger.info(f"AnimeAPIService: Searching anime for query: '{query}', page: {page}")
        params = {"q": query, "page": page}
        return self._make_request("/api/search", params=params)

    def get_anime_details(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches details for a specific anime.
        Corresponds to GET /api/anime/{id}.
        """
        logger.info(f"AnimeAPIService: Fetching details for anime ID: {anime_id}")
        return self._make_request(f"/api/anime/{anime_id}")

    def get_anime_info(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches comprehensive anime information (details, episodes, etc.)
        Corresponds to GET /api/info/{id} from the Node.js API.
        This endpoint provides the most complete initial data for an anime.
        """
        logger.info(f"AnimeAPIService: Fetching comprehensive info for anime ID: {anime_id} using /api/info.")
        return self._make_request(f"/api/info/{anime_id}")

    def get_anime_by_category(self, category: str, page: int = 1, limit: int = 20) -> tuple[dict, int]:
        """
        Fetches a list of anime by category.
        Corresponds to GET /api/{category_name}?page={page}&limit={limit}.
        """
        logger.info(f"AnimeAPIService: Fetching anime for category: {category}, page: {page}, limit: {limit}")
        params = {"page": page, "limit": limit}
        # The category name might contain slashes (e.g., 'genre/action'), so it needs to be part of the path
        # and correctly URL-encoded by requests.
        return self._make_request(f"/api/{category}", params=params) # CORRECTED LINE

    def get_episode_list(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches the list of episodes for a given anime ID.
        Corresponds to GET /api/episode/{id} from the Node.js API.
        """
        logger.info(f"AnimeAPIService: Fetching episode list for anime ID: {anime_id}")
        return self._make_request(f"/api/episode/{anime_id}")

    def get_characters_list(self, anime_id: str, page: int = 1) -> tuple[dict, int]:
        """
        Fetches the list of characters for a given anime ID.
        Corresponds to GET /api/characters/{id}?page={page} from the Node.js API.
        """
        logger.info(f"AnimeAPIService: Fetching characters list for anime ID: {anime_id}, page: {page}")
        params = {"page": page}
        return self._make_request(f"/api/characters/{anime_id}", params=params)

    def get_related_anime(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches related anime for a given anime ID.
        Corresponds to GET /api/related/{id} from the Node.js API.
        """
        logger.info(f"AnimeAPIService: Fetching related anime for anime ID: {anime_id}")
        return self._make_request(f"/api/related/{anime_id}")

    def get_recommended_anime(self, anime_id: str) -> tuple[dict, int]:
        """
        Fetches recommended anime for a given anime ID.
        Corresponds to GET /api/recommendations/{id} from the Node.js API.
        """
        logger.info(f"AnimeAPIService: Fetching recommended anime for anime ID: {anime_id}")
        return self._make_request(f"/api/recommendations/{anime_id}")

    def get_streaming_info(self, anime_id: str, server: str, stream_type: str = "sub") -> tuple[dict, int]:
        """
        Fetches streaming information for an anime episode.
        Corresponds to GET /api/stream?id={string}&server={string}&type={string}.
        """
        logger.info(f"AnimeAPIService: Fetching streaming info for ID: {anime_id}, server: {server}, type: {stream_type}")
        params = {"id": anime_id, "server": server, "type": stream_type}
        return self._make_request("/api/stream", params=params)

    def get_available_servers(self, anime_id: str, episode_id: str = None) -> tuple[dict, int]:
        """
        Fetches available servers for an anime episode.
        Corresponds to GET /api/servers/{id}?ep={number}.
        """
        logger.info(f"AnimeAPIService: Fetching available servers for anime ID: {anime_id}, episode ID: {episode_id}")
        params = {}
        if episode_id:
            params['ep'] = episode_id
        return self._make_request(f"/api/servers/{anime_id}", params=params)

    def get_character_details(self, character_id: str) -> tuple[dict, int]:
        """
        Fetches details for a specific character.
        Corresponds to GET /api/character/{character-id}.
        """
        logger.info(f"AnimeAPIService: Fetching details for character ID: {character_id}")
        return self._make_request(f"/api/character/{character_id}")

    def get_voice_actor_details(self, actor_id: str) -> tuple[dict, int]:
        """
        Fetches details for a specific voice actor.
        Corresponds to GET /api/actors/{voice-actor-id}.
        """
        logger.info(f"AnimeAPIService: Fetching details for voice actor ID: {actor_id}")
        return self._make_request(f"/api/actors/{actor_id}")

    def get_qtip_info(self, qtip_id: int) -> tuple[dict, int]:
        """
        Fetches Qtip information for a specific anime (often related to quick info display).
        Corresponds to GET /api/qtip/{id}.
        """
        logger.info(f"AnimeAPIService: Fetching Qtip info for ID: {qtip_id}")
        return self._make_request(f"/api/qtip/{qtip_id}")

