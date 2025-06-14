# backend/services/one_piece_api_service.py
import requests
import logging
from typing import List, Dict, Any, Optional, Tuple

from config import Config

logger = logging.getLogger(__name__)

class OnePieceAPIService:
    """
    Service to interact with the One Piece API.
    """
    def __init__(self):
        self.base_url = Config.ONE_PIECE_API_BASE_URL
        logger.info(f"OnePieceAPIService: Initialized with base URL: {self.base_url}")

    def _make_request(self, endpoint: str) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        """
        Helper method to make a GET request to the One Piece API.
        Args:
            endpoint (str): The API endpoint (e.g., "/sagas/en").
        Returns:
            Tuple[Optional[List[Dict[str, Any]]], int]: A tuple containing a list of dictionaries
            (data) or None if an error occurred, and the HTTP status code.
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"OnePieceAPIService: Making request to {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if not isinstance(data, list):
                logger.warning(f"OnePieceAPIService: Unexpected response format for {url}. Expected a list, got {type(data)}.")
                return None, 500
            logger.debug(f"OnePieceAPIService: Successfully fetched data from {url}")
            return data, response.status_code
        except requests.exceptions.Timeout:
            logger.error(f"OnePieceAPIService: Request to {url} timed out.")
            return None, 408 # Request Timeout
        except requests.exceptions.ConnectionError as e:
            logger.error(f"OnePieceAPIService: Connection error to {url}: {e}")
            return None, 503 # Service Unavailable
        except requests.exceptions.HTTPError as e:
            logger.error(f"OnePieceAPIService: HTTP error from {url}: {e.response.status_code} - {e.response.text}")
            return None, e.response.status_code
        except Exception as e:
            logger.error(f"OnePieceAPIService: An unexpected error occurred while fetching from {url}: {e}")
            return None, 500

    def get_sagas(self) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        """
        Fetches all One Piece sagas.
        Returns:
            Tuple[Optional[List[Dict[str, Any]]], int]: A tuple containing a list of saga dictionaries
            or None, and the HTTP status code.
        """
        logger.info("OnePieceAPIService: Fetching One Piece sagas...")
        return self._make_request("/sagas/en")

    def get_characters(self) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        """
        Fetches all One Piece characters.
        Returns:
            Tuple[Optional[List[Dict[str, Any]]], int]: A tuple containing a list of character dictionaries
            or None, and the HTTP status code.
        """
        logger.info("OnePieceAPIService: Fetching One Piece characters...")
        return self._make_request("/characters/en")

    def get_fruits(self) -> Tuple[Optional[List[Dict[str, Any]]], int]:
        """
        Fetches all One Piece devil fruits.
        Returns:
            Tuple[Optional[List[Dict[str, Any]]], int]: A tuple containing a list of fruit dictionaries
            or None, and the HTTP status code.
        """
        logger.info("OnePieceAPIService: Fetching One Piece fruits...")
        return self._make_request("/fruits/en")
