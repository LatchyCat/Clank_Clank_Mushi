# backend/services/one_piece_api_service.py
import requests
from config import Config

class OnePieceAPIService:
    """
    Service class for interacting with the One Piece API.
    """
    BASE_URL = Config.ONE_PIECE_API_BASE_URL # From config.py

    @staticmethod
    def _make_request(endpoint, params=None):
        """Helper method to make a GET request to the One Piece API."""
        url = f"{OnePieceAPIService.BASE_URL}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred while fetching from One Piece API ({url}): {e}")
            # print(f"Response content: {e.response.text}") # Uncomment for more detailed error
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error occurred while fetching from One Piece API ({url}): {e}")
            return None
        except requests.exceptions.Timeout:
            print(f"Request to One Piece API timed out ({url}).")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred while fetching from One Piece API ({url}): {e}")
            return None

    @staticmethod
    def get_all_sagas():
        """
        Retrieves all One Piece sagas.
        Endpoint: GET /v2/sagas/en
        """
        endpoint = "/sagas/en"
        return OnePieceAPIService._make_request(endpoint)

    @staticmethod
    def get_all_characters():
        """
        Retrieves all One Piece characters.
        Endpoint: GET /v2/characters/en
        """
        endpoint = "/characters/en"
        return OnePieceAPIService._make_request(endpoint)

    @staticmethod
    def get_all_fruits():
        """
        Retrieves all One Piece fruits (Devil Fruits).
        Endpoint: GET /v2/fruits/en
        """
        endpoint = "/fruits/en"
        return OnePieceAPIService._make_request(endpoint)

    # You can add more specific endpoints here as needed (e.g., /characters/en/{id}, /fruits/en/{id})
