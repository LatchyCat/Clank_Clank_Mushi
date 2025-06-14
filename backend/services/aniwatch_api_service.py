# backend/services/aniwatch_api_service.py
import requests
import logging

from config import Config

logger = logging.getLogger(__name__)

class AniwatchAPIService:
    """
    Service class for interacting with your locally hosted Aniwatch API (itzzzme/anime-api fork).
    Handles constructing and sending HTTP requests to the Aniwatch API.
    """
    # Base URL points to the new /api prefix of the itzzzme/anime-api fork
    BASE_URL = Config.ANIWATCH_API_BASE_URL + "/api"

    def _make_request(self, endpoint: str, params: dict = None) -> tuple[dict | None, int]:
        """
        Helper method to make GET requests to the Aniwatch API.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        logger.debug(f"AniwatchAPIService: Making request to: {url} with params: {params}")
        try:
            response = requests.get(url, params=params, timeout=30)
            # The itzzzme/anime-api might return 404 with its own HTML,
            # so we catch HTTPError and return the HTML as part of the error message
            response.raise_for_status()
            # The itzzzme/anime-api also uses a 'success' field in its JSON responses
            json_response = response.json()
            if json_response.get("success"):
                return json_response.get("data"), response.status_code
            else:
                # If 'success' is false, it might still provide an error message in data
                error_detail = json_response.get("data", {}).get("message", "Unknown error from Aniwatch API")
                logger.error(f"AniwatchAPIService: API returned success:false for {url}: {error_detail}")
                return {"error": error_detail}, response.status_code
        except requests.exceptions.HTTPError as e:
            error_body = e.response.text if e.response else "No response body"
            logger.error(f"AniwatchAPIService: HTTP error for {url}: {e.response.status_code} - {error_body}")
            return {"error": f"HTTP error: {e.response.status_code} - {error_body}"}, e.response.status_code
        except requests.exceptions.ConnectionError as e:
            logger.error(f"AniwatchAPIService: Connection error to {url}: {e}")
            return {"error": f"Connection error to Aniwatch API: {e}. Ensure the Aniwatch API is running at {Config.ANIWATCH_API_BASE_URL}."}, 503
        except requests.exceptions.Timeout:
            logger.error(f"AniwatchAPIService: Request to {url} timed out.")
            return {"error": "Aniwatch API request timed out."}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"AniwatchAPIService: An unexpected request error occurred for {url}: {e}")
            return {"error": f"An unexpected error occurred with Aniwatch API request: {e}"}, 500
        except Exception as e:
            logger.error(f"AniwatchAPIService: An unexpected error occurred: {e}")
            return {"error": f"An unexpected error occurred: {e}"}, 500

    # Refactored: Consolidated A-Z, Genre, and Category lists into one method
    def get_list_by_category_or_genre(self, route_type: str, page: int = 1) -> tuple[dict | None, int]:
        """
        Fetches lists of anime by various categories (top-airing, most-popular, tv, etc.)
        or by genre (action, adventure, etc.) or A-Z list (az-list, az-list/a, etc.).
        Corresponds to /api/{routeType} in itzzzme/anime-api.
        """
        endpoint = f"{route_type}"
        params = {"page": page}
        data, status = self._make_request(endpoint, params)
        # The itzzzme/anime-api returns data directly, not nested under a 'data' key for these
        if status == 200 and data:
            return data, status # Returns the raw data structure directly
        return data, status

    def get_anime_qtip_info(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches detailed 'qtip' information for a specific anime ID.
        Corresponds to /api/qtip/:id in itzzzme/anime-api.
        """
        endpoint = f"qtip/{anime_id}" # ID is a path parameter
        data, status = self._make_request(endpoint)
        if status == 200 and data: # Qtip returns "anime" object nested under "data"
            return data, status
        return data, status

    def get_anime_details_full_info(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches detailed 'about info' (full details) for a specific anime ID.
        Corresponds to /api/info?id={animeId} in itzzzme/anime-api. (ID is a query parameter here)
        """
        endpoint = "info"
        params = {"id": anime_id} # ID is a query parameter
        data, status = self._make_request(endpoint, params)
        if status == 200 and data:
            return data, status
        return data, status

    def get_anime_home_page(self) -> tuple[dict | None, int]:
        """
        Fetches the anime home page data from Aniwatch API.
        Corresponds to /api in itzzzme/anime-api (or /api/home if exists - based on import, it's just /api)
        """
        endpoint = "" # Root of /api
        data, status = self._make_request(endpoint)
        if status == 200 and data:
            return data, status
        return data, status

    def search_anime(
        self,
        query: str,
        page: int = 1,
        genres: str = None, # Comma separated genre IDs from their map
        type: str = None,    # Mapped type ID
        sort: str = None,    # Mapped sort type
        season: str = None,  # Mapped season ID
        language: str = None,# Mapped language ID
        status: str = None,  # Mapped status ID
        rated: str = None,   # Mapped rated ID
        start_date: str = None, # yyyy-mm-dd
        end_date: str = None, # yyyy-mm-dd
        score: str = None    # Mapped score ID
    ) -> tuple[dict | None, int]:
        """
        Searches for anime titles on Aniwatch with advanced filtering options.
        Corresponds to /api/search in itzzzme/anime-api.
        """
        endpoint = "search"
        params = {"keyw": query, "page": page} # itzzzme/anime-api uses 'keyw' for query
        if genres: params["genre"] = genres # itzzzme uses 'genre'
        if type: params["type"] = type
        if sort: params["sort"] = sort
        if season: params["season"] = season
        if language: params["lang"] = language # itzzzme uses 'lang'
        if status: params["status"] = status
        if rated: params["rated"] = rated
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if score: params["score"] = score

        data, status = self._make_request(endpoint, params)
        if status == 200 and data:
            return data, status
        return data, status

    def get_search_suggestions(self, query: str) -> tuple[dict | None, int]:
        """
        Fetches search suggestions from Aniwatch API.
        Corresponds to /api/search/suggest?keyw={query} in itzzzme/anime-api.
        """
        endpoint = "search/suggest"
        params = {"keyw": query} # itzzzme/anime-api uses 'keyw' for query
        data, status = self._make_request(endpoint, params)
        if status == 200 and data:
            return data, status
        return data, status

    def get_producer_animes(self, name: str, page: int = 1) -> tuple[dict | None, int]:
        """
        Fetches anime by producer name from Aniwatch API.
        Corresponds to /api/producer/:id?page={page} in itzzzme/anime-api.
        """
        endpoint = f"producer/{name}" # 'name' is the ID in path
        params = {"page": page}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data:
            return data, status
        return data, status

    # Removed old get_genre_animes and get_category_animes.
    # Use get_list_by_category_or_genre instead.

    def get_estimated_schedules(self, date: str) -> tuple[dict | None, int]:
        """
        Fetches estimated schedules for anime from Aniwatch API.
        Corresponds to /api/schedule?date={date} in itzzzme/anime-api.
        """
        endpoint = "schedule"
        params = {"date": date}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data:
            return data, status
        return data, status

    def get_anime_episodes(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches episodes for a specific anime ID from Aniwatch API.
        Corresponds to /api/episodes/:id in itzzzme/anime-api.
        """
        endpoint = f"episodes/{anime_id}" # ID is a path parameter
        data, status = self._make_request(endpoint)
        if status == 200 and data:
            return data, status
        return data, status

    def get_anime_next_episode_schedule(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches the next episode schedule for a specific anime ID.
        Corresponds to /api/schedule/:id in itzzzme/anime-api.
        """
        endpoint = f"schedule/{anime_id}" # ID is a path parameter
        data, status = self._make_request(endpoint)
        if status == 200 and data:
            return data, status
        return data, status

    def get_anime_episode_servers(self, anime_episode_id: str) -> tuple[dict | None, int]:
        """
        Fetches episode streaming servers for a given episode ID.
        Corresponds to /api/servers/:id in itzzzme/anime-api.
        """
        endpoint = f"servers/{anime_episode_id}" # Episode ID is a path parameter
        data, status = self._make_request(endpoint)
        if status == 200 and data:
            return data, status
        return data, status

    def get_anime_episode_streaming_links(self, anime_episode_id: str, server: str = None, category: str = None) -> tuple[dict | None, int]:
        """
        Fetches episode streaming links for a given episode ID, server, and category.
        Corresponds to /api/stream?id={id}&server={server}&category={dub || sub || raw} in itzzzme/anime-api.
        """
        endpoint = "stream"
        params = {"id": anime_episode_id} # itzzzme uses 'id' for episode ID query param
        if server:
            params["server"] = server
        if category:
            params["category"] = category
        data, status = self._make_request(endpoint, params)
        if status == 200 and data:
            return data, status
        return data, status
