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

    def _make_request(self, endpoint: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        A more robust request handler that always returns a list.
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"OnePieceAPIService: Making request to {url}")
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list):
                logger.warning(f"OnePieceAPIService: Unexpected response format for {url}. Expected a list, got {type(data)}. Returning empty list.")
                return [], response.status_code
            logger.debug(f"OnePieceAPIService: Successfully fetched {len(data)} items from {url}")
            return data, response.status_code
        except requests.exceptions.Timeout:
            logger.error(f"OnePieceAPIService: Request to {url} timed out.")
            return [], 408
        except requests.exceptions.ConnectionError as e:
            logger.error(f"OnePieceAPIService: Connection error to {url}: {e}")
            return [], 503
        except requests.exceptions.HTTPError as e:
            logger.error(f"OnePieceAPIService: HTTP error from {url}: {e.response.status_code} - {e.response.text}")
            return [], e.response.status_code
        except Exception as e:
            logger.error(f"OnePieceAPIService: An unexpected error occurred while fetching from {url}: {e}", exc_info=True)
            return [], 500

    def get_characters(self) -> Tuple[List[Dict[str, Any]], int]:
        logger.info("OnePieceAPIService: Fetching One Piece characters...")
        return self._make_request("/characters/en")

    def get_fruits(self) -> Tuple[List[Dict[str, Any]], int]:
        logger.info("OnePieceAPIService: Fetching One Piece fruits...")
        return self._make_request("/fruits/en")
