# backend/services/aniwatch_api_service.py
import requests
import logging

from config import Config

logger = logging.getLogger(__name__)

class AniwatchAPIService:
    """
    Service class for interacting with your locally hosted Aniwatch API.
    Handles constructing and sending HTTP requests to the Aniwatch API.
    """
    BASE_URL = Config.ANIWATCH_API_BASE_URL + "/api/v2/hianime" # Base path for hi-anime endpoints

    def _make_request(self, endpoint: str, params: dict = None) -> tuple[dict | None, int]:
        """
        Helper method to make GET requests to the Aniwatch API.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        logger.debug(f"AniwatchAPIService: Making request to: {url} with params: {params}")
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json(), response.status_code
        except requests.exceptions.HTTPError as e:
            logger.error(f"AniwatchAPIService: HTTP error for {url}: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}, e.response.status_code
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

    def get_az_list(self, sort_option: str = "all", page: int = 1) -> tuple[dict | None, int]:
        """
        Fetches the A-Z list of anime from Aniwatch API.
        sort_option: "all", "other", "0-9", or any English alphabet (e.g., "A", "B").
        """
        endpoint = f"azlist/{sort_option}"
        params = {"page": page}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status # Return error data/status if not successful

    def get_anime_qtip_info(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches detailed 'qtip' information for a specific anime ID.
        Corresponds to /api/v2/hianime/qtip/{animeId}
        """
        endpoint = f"qtip/{anime_id}"
        data, status = self._make_request(endpoint)
        if status == 200 and data and data.get("success"):
            return data.get("data", {}).get("anime"), status # Qtip returns "anime" object nested under "data"
        return data, status # Return error data/status if not successful

    def get_anime_details_full_info(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches detailed 'about info' (full details) for a specific anime ID.
        Corresponds to /api/v2/hianime/anime/{animeId}
        """
        endpoint = f"anime/{anime_id}"
        data, status = self._make_request(endpoint)
        if status == 200 and data and data.get("success"):
            # The schema shows 'anime' as a list with 'info' and 'moreInfo'
            anime_data = data.get("data", {}).get("anime")
            if anime_data and isinstance(anime_data, list) and len(anime_data) > 0:
                combined_info = {}
                # Combine info and moreInfo dictionaries
                if "info" in anime_data[0]:
                    combined_info.update(anime_data[0]["info"])
                if "moreInfo" in anime_data[0]:
                    combined_info.update(anime_data[0]["moreInfo"])

                # Also include top-level data like mostPopularAnimes, recommendedAnimes, etc.
                # but only if needed for embedding or direct display by controller
                # For now, we'll return the combined info and other top-level lists separately if present
                full_details = {
                    "main_info": combined_info,
                    "mostPopularAnimes": data.get("data", {}).get("mostPopularAnimes"),
                    "recommendedAnimes": data.get("data", {}).get("recommendedAnimes"),
                    "relatedAnimes": data.get("data", {}).get("relatedAnimes"),
                    "seasons": data.get("data", {}).get("seasons")
                }
                return full_details, status
            return anime_data, status # Return raw anime_data if not in expected format
        return data, status # Return error data/status if not successful

    def get_anime_home_page(self) -> tuple[dict | None, int]:
        """
        Fetches the anime home page data from Aniwatch API.
        Corresponds to /api/v2/hianime/home
        """
        endpoint = "home"
        data, status = self._make_request(endpoint)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def search_anime(
        self,
        query: str,
        page: int = 1,
        genres: str = None,
        type: str = None,
        sort: str = None,
        season: str = None,
        language: str = None,
        status: str = None,
        rated: str = None,
        start_date: str = None,
        end_date: str = None,
        score: str = None
    ) -> tuple[dict | None, int]:
        """
        Searches for anime titles on Aniwatch with advanced filtering options.
        Corresponds to /api/v2/hianime/search
        """
        endpoint = "search"
        params = {"q": query, "page": page}
        if genres: params["genres"] = genres
        if type: params["type"] = type
        if sort: params["sort"] = sort
        if season: params["season"] = season
        if language: params["language"] = language
        if status: params["status"] = status
        if rated: params["rated"] = rated
        if start_date: params["start_date"] = start_date
        if end_date: params["end_date"] = end_date
        if score: params["score"] = score

        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_search_suggestions(self, query: str) -> tuple[dict | None, int]:
        """
        Fetches search suggestions from Aniwatch API.
        Corresponds to /api/v2/hianime/search/suggestion
        """
        endpoint = "search/suggestion"
        params = {"q": query}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_producer_animes(self, name: str, page: int = 1) -> tuple[dict | None, int]:
        """
        Fetches anime by producer name from Aniwatch API.
        Corresponds to /api/v2/hianime/producer/{name}
        """
        endpoint = f"producer/{name}"
        params = {"page": page}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_genre_animes(self, name: str, page: int = 1) -> tuple[dict | None, int]:
        """
        Fetches anime by genre name from Aniwatch API.
        Corresponds to /api/v2/hianime/genre/{name}
        """
        endpoint = f"genre/{name}"
        params = {"page": page}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_category_animes(self, category: str, page: int = 1) -> tuple[dict | None, int]:
        """
        Fetches anime by category from Aniwatch API.
        Corresponds to /api/v2/hianime/category/{name}
        """
        endpoint = f"category/{category}"
        params = {"page": page}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_estimated_schedules(self, date: str) -> tuple[dict | None, int]:
        """
        Fetches estimated schedules for anime from Aniwatch API.
        Corresponds to /api/v2/hianime/schedule?date={date}
        """
        endpoint = "schedule"
        params = {"date": date}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_anime_episodes(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches episodes for a specific anime ID from Aniwatch API.
        Corresponds to /api/v2/hianime/anime/{animeId}/episodes
        """
        endpoint = f"anime/{anime_id}/episodes"
        data, status = self._make_request(endpoint)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_anime_next_episode_schedule(self, anime_id: str) -> tuple[dict | None, int]:
        """
        Fetches the next episode schedule for a specific anime ID.
        Corresponds to /api/v2/hianime/anime/{animeId}/next-episode-schedule
        """
        endpoint = f"anime/{anime_id}/next-episode-schedule"
        data, status = self._make_request(endpoint)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_anime_episode_servers(self, anime_episode_id: str) -> tuple[dict | None, int]:
        """
        Fetches episode streaming servers for a given episode ID.
        Corresponds to /api/v2/hianime/episode/servers?animeEpisodeId={id}
        """
        endpoint = "episode/servers"
        params = {"animeEpisodeId": anime_episode_id}
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status

    def get_anime_episode_streaming_links(self, anime_episode_id: str, server: str = None, category: str = None) -> tuple[dict | None, int]:
        """
        Fetches episode streaming links for a given episode ID, server, and category.
        Corresponds to /api/v2/hianime/episode/sources?animeEpisodeId={id}?server={server}&category={dub || sub || raw}
        """
        endpoint = "episode/sources"
        params = {"animeEpisodeId": anime_episode_id}
        if server:
            params["server"] = server
        if category:
            params["category"] = category
        data, status = self._make_request(endpoint, params)
        if status == 200 and data and data.get("success"):
            return data.get("data"), status
        return data, status
