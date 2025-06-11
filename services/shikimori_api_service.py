# backend/services/shikimori_api_service.py (CORRECTED AGAIN)
import requests
import json
import logging

from config import Config

# Configure logging for this module
logger = logging.getLogger(__name__)

class ShikimoriAPIService:
    """
    Service class for interacting with the Shikimori GraphQL API.
    Handles constructing and sending GraphQL queries.
    """
    BASE_URL = Config.SHIKIMORI_API_BASE_URL + "/api/graphql" # Ensure this is the GraphQL endpoint
    ACCESS_TOKEN = Config.SHIKIMORI_ACCESS_TOKEN # For authenticated requests

    # GraphQL Queries (updated based on Shikimori's schema expectations)
    # The 'query' keyword is part of the GraphQL syntax itself.

    _ANIME_SEARCH_QUERY = """
    query AnimeSearch($search: String!, $limit: Int!) {
        animes(search: $search, limit: $limit) {
            id
            name
            russian
            airedOn {
                year
            }
            poster {
                mainUrl # CORRECTED: Use mainUrl or originalUrl
            }
        }
    }
    """

    # Corrected: Use 'animes(ids: [$id])' for details and fetch the first result
    _ANIME_DETAILS_QUERY = """
    query AnimeDetails($id: Int!) {
        animes(ids: [$id]) { # CORRECTED: Use plural 'animes' with 'ids' filter
            id
            name
            russian
            kind
            episodes
            status
            airedOn {
                date
                year
            }
            releasedOn {
                date
            }
            poster {
                originalUrl
                mainUrl
            }
            description
            descriptionHtml
            descriptionSource
        }
    }
    """

    _ANIME_RECENT_QUERY = """
    query RecentAnimes($limit: Int!) {
        animes(order: CREATED_AT_DESC, limit: $limit) { # CORRECTED: Changed order to CREATED_AT_DESC
            id
            name
            russian
            airedOn {
                year
            }
            status
            poster {
                mainUrl # CORRECTED: Use mainUrl or originalUrl
            }
        }
    }
    """

    _MANGA_SEARCH_QUERY = """
    query MangaSearch($search: String!, $limit: Int!) {
        mangas(search: $search, limit: $limit) {
            id
            name
            russian
            volumes
            chapters
            status
            poster {
                mainUrl # CORRECTED: Use mainUrl or originalUrl
            }
        }
    }
    """

    _MANGA_RECENT_QUERY = """
    query RecentMangas($limit: Int!) {
        mangas(order: CREATED_AT_DESC, limit: $limit) { # CORRECTED: Changed order to CREATED_AT_DESC
            id
            name
            russian
            volumes
            chapters
            status
            poster {
                mainUrl # CORRECTED: Use mainUrl or originalUrl
            }
        }
    }
    """

    _CHARACTER_SEARCH_QUERY = """
    query CharacterSearch($search: String!, $limit: Int!) {
        characters(search: $search, limit: $limit) {
            id
            name
            russian
            poster {
                mainUrl # CORRECTED: Use mainUrl or originalUrl
            }
        }
    }
    """

    # Corrected: Use 'characters(ids: [$id])' for details
    _CHARACTER_DETAILS_QUERY = """
    query CharacterDetails($id: Int!) {
        characters(ids: [$id]) { # CORRECTED: Use plural 'characters' with 'ids' filter
            id
            name
            russian
            description
            descriptionHtml
            descriptionSource
            poster { # ADDED POSTER FIELD
                originalUrl
                mainUrl
            }
        }
    }
    """

    # Corrected: Removed non-existent fields from Person search query, fixed poster field
    _PERSON_SEARCH_QUERY = """
    query PersonSearch($search: String!, $limit: Int!) {
        people(search: $search, limit: $limit) {
            id
            name
            russian
            poster {
                mainUrl # CORRECTED: Use mainUrl or originalUrl
            }
        }
    }
    """

    # Corrected: Use 'people(ids: [$id])' for details, fixed poster field
    _PERSON_DETAILS_QUERY = """
    query PersonDetails($id: Int!) {
        people(ids: [$id]) { # CORRECTED: Use plural 'people' with 'ids' filter
            id
            name
            russian
            website
            poster {
                originalUrl
                mainUrl
            }
        }
    }
    """

    @staticmethod
    def _make_graphql_request(query: str, variables: dict = None):
        """Helper method to make a POST request to the Shikimori GraphQL API."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ClankClankMushi/1.0 (https://github.com/your-repo-link; your-email@example.com)" # REMEMBER TO UPDATE THIS
        }

        if ShikimoriAPIService.ACCESS_TOKEN:
            headers["Authorization"] = f"Bearer {ShikimoriAPIService.ACCESS_TOKEN}"
        else:
            logger.warning("Shikimori ACCESS_TOKEN not configured. Requests requiring authentication may fail for protected endpoints.")

        payload = {
            "query": query,
            "variables": variables if variables is not None else {}
        }

        logger.debug(f"ShikimoriAPIService: Making GraphQL request to: {ShikimoriAPIService.BASE_URL}")
        try:
            response = requests.post(ShikimoriAPIService.BASE_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if 'errors' in data:
                logger.error(f"Shikimori GraphQL errors: {data['errors']}")
                return {"error": "GraphQL Error", "details": data['errors']}, 500

            return data, 200

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching from Shikimori API ({ShikimoriAPIService.BASE_URL}): {e}")
            logger.error(f"Response content: {e.response.text}")
            return {"error": f"HTTP Error: {e.response.status_code}", "details": e.response.text}, e.response.status_code
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error occurred while fetching from Shikimori API ({ShikimoriAPIService.BASE_URL}): {e}")
            return {"error": "Connection Error", "details": str(e)}, 503
        except requests.exceptions.Timeout:
            logger.error(f"Request to Shikimori API timed out ({ShikimoriAPIService.BASE_URL}).")
            return {"error": "Request Timed Out"}, 504
        except requests.exceptions.RequestException as e:
            logger.error(f"An unexpected error occurred while fetching from Shikimori API ({ShikimoriAPIService.BASE_URL}): {e}")
            return {"error": "Unexpected Request Error", "details": str(e)}, 500
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON response from Shikimori API: {response.text}")
            return {"error": "Invalid JSON Response"}, 500

    @staticmethod
    def search_animes(query: str, limit: int = 10):
        logger.debug(f"ShikimoriAPIService: Searching anime for '{query}' (limit={limit})...")
        variables = {"search": query, "limit": limit}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._ANIME_SEARCH_QUERY, variables)
        if status != 200:
            return None # Indicate error to controller
        return data.get('data', {}).get('animes')

    @staticmethod
    def get_anime_details(anime_id: int):
        logger.debug(f"ShikimoriAPIService: Fetching details for anime ID: {anime_id}...")
        variables = {"id": anime_id}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._ANIME_DETAILS_QUERY, variables)
        if status != 200:
            return None
        # When using animes(ids: [$id]), the response will be a list, even for a single ID
        return data.get('data', {}).get('animes') # Expecting a list here

    @staticmethod
    def get_recent_animes(limit: int = 10):
        logger.debug(f"ShikimoriAPIService: Fetching recent animes (limit={limit})...")
        variables = {"limit": limit}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._ANIME_RECENT_QUERY, variables)
        if status != 200:
            return None
        return data.get('data', {}).get('animes')

    @staticmethod
    def search_mangas(query: str, limit: int = 10):
        logger.debug(f"ShikimoriAPIService: Searching manga for '{query}' (limit={limit})...")
        variables = {"search": query, "limit": limit}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._MANGA_SEARCH_QUERY, variables)
        if status != 200:
            return None
        return data.get('data', {}).get('mangas')

    @staticmethod
    def get_recent_mangas(limit: int = 10):
        logger.debug(f"ShikimoriAPIService: Fetching recent mangas (limit={limit})...")
        variables = {"limit": limit}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._MANGA_RECENT_QUERY, variables)
        if status != 200:
            return None
        return data.get('data', {}).get('mangas')

    @staticmethod
    def search_characters(query: str, limit: int = 10):
        logger.debug(f"ShikimoriAPIService: Searching characters for '{query}' (limit={limit})...")
        variables = {"search": query, "limit": limit}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._CHARACTER_SEARCH_QUERY, variables)
        if status != 200:
            return None
        return data.get('data', {}).get('characters')

    @staticmethod
    def get_character_details(character_id: int):
        logger.debug(f"ShikimoriAPIService: Fetching details for character ID: {character_id}...")
        variables = {"id": character_id}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._CHARACTER_DETAILS_QUERY, variables)
        if status != 200:
            return None
        # When using characters(ids: [$id]), the response will be a list
        return data.get('data', {}).get('characters') # Expecting a list here

    @staticmethod
    def search_people(query: str, limit: int = 10):
        logger.debug(f"ShikimoriAPIService: Searching people for '{query}' (limit={limit})...")
        variables = {"search": query, "limit": limit}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._PERSON_SEARCH_QUERY, variables)
        if status != 200:
            return None
        return data.get('data', {}).get('people')

    @staticmethod
    def get_person_details(person_id: int):
        logger.debug(f"ShikimoriAPIService: Fetching details for person ID: {person_id}...")
        variables = {"id": person_id}
        data, status = ShikimoriAPIService._make_graphql_request(ShikimoriAPIService._PERSON_DETAILS_QUERY, variables)
        if status != 200:
            return None
        # When using people(ids: [$id]), the response will be a list
        return data.get('data', {}).get('people') # Expecting a list here
