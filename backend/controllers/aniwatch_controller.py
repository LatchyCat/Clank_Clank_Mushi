# backend/controllers/aniwatch_controller.py
import logging
from services.aniwatch_api_service import AniwatchAPIService

logger = logging.getLogger(__name__)

class AniwatchController:
    """
    Controller for handling data from the Aniwatch API.
    It primarily acts as an intermediary, calling the AniwatchAPIService
    to fetch raw data and then potentially formatting it for further use
    or direct API responses.
    """
    def __init__(self):
        self.aniwatch_service = AniwatchAPIService()
        logger.info("AniwatchController: Initialized.")

    def get_aniwatch_az_list_data(self, sort_option: str = "all", page: int = 1):
        """
        Fetches the A-Z anime list from Aniwatch API.
        Args:
            sort_option (str): How to sort the list (e.g., "all", "trending", "popular").
            page (int): The page number.
        Returns:
            tuple[dict, int]: The JSON response data and HTTP status code.
        """
        logger.debug(f"AniwatchController: Fetching A-Z list for sort_option='{sort_option}', page={page}.")
        data, status_code = self.aniwatch_service.get_az_list(sort_option=sort_option, page=page)
        return data, status_code

    def get_aniwatch_anime_details_data(self, anime_id: str):
        """
        Fetches detailed information for a specific anime from Aniwatch API.
        Args:
            anime_id (str): The ID of the anime.
        Returns:
            tuple[dict, int]: The JSON response data and HTTP status code.
        """
        logger.debug(f"AniwatchController: Fetching details for anime ID='{anime_id}'.")
        data, status_code = self.aniwatch_service.get_anime_info(anime_id=anime_id)
        return data, status_code

    def get_aniwatch_trending_anime_data(self):
        """
        Fetches trending anime from Aniwatch API.
        Returns:
            tuple[dict, int]: The JSON response data and HTTP status code.
        """
        logger.debug("AniwatchController: Fetching trending anime.")
        data, status_code = self.aniwatch_service.get_trending()
        return data, status_code

    def get_aniwatch_popular_anime_data(self):
        """
        Fetches popular anime from Aniwatch API.
        Returns:
            tuple[dict, int]: The JSON response data and HTTP status code.
        """
        logger.debug("AniwatchController: Fetching popular anime.")
        data, status_code = self.aniwatch_service.get_popular()
        return data, status_code

    def search_aniwatch_anime_data(self, keyword: str):
        """
        Searches anime on Aniwatch API by keyword.
        Args:
            keyword (str): The search term.
        Returns:
            tuple[dict, int]: The JSON response data and HTTP status code.
        """
        logger.debug(f"AniwatchController: Searching Aniwatch for keyword='{keyword}'.")
        data, status_code = self.aniwatch_service.search_anime(query=keyword)
        return data, status_code
